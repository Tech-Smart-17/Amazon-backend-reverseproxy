"""Admin-only natural-language SQL agent with a read-only database view."""
from functools import lru_cache
import asyncio

from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url

from app.config import settings
from app.services.langchain_runtime import get_chat_model, message_text


SQL_AGENT_TABLES = ("products", "categories", "inventory")


def _validate_select(query: str, dialect: str) -> str:
    """Accept one SELECT statement that only references explicitly allowed tables."""
    import sqlglot
    from sqlglot import exp

    try:
        statements = sqlglot.parse(query, read=dialect)
    except Exception as exc:
        raise ValueError("The query is not valid SQL for this database.") from exc
    if len(statements) != 1 or not isinstance(statements[0], exp.Select):
        raise ValueError("Only a single SELECT query is allowed.")

    statement = statements[0]
    cte_names = {
        cte.alias_or_name.lower()
        for cte in statement.find_all(exp.CTE)
        if cte.alias_or_name
    }
    allowed_names = {name.lower() for name in SQL_AGENT_TABLES} | cte_names
    referenced_tables = {
        table.name.lower() for table in statement.find_all(exp.Table) if table.name
    }
    if not referenced_tables.issubset(allowed_names):
        raise ValueError("The query references tables outside the allowed catalog.")

    if statement.args.get("limit") is None:
        statement = statement.limit(100)
    return statement.sql(dialect=dialect)


@lru_cache(maxsize=1)
def get_readonly_sql_database():
    """Create a sync SQLDatabase over the app database with write protection."""
    from langchain_community.utilities import SQLDatabase

    url = make_url(settings.DATABASE_URL)
    if url.drivername == "sqlite+aiosqlite":
        url = url.set(drivername="sqlite")
    elif url.drivername in ("postgresql", "postgresql+asyncpg"):
        url = url.set(drivername="postgresql+psycopg")
    elif not url.drivername.startswith(("sqlite", "postgresql+psycopg")):
        raise RuntimeError("The SQL agent supports SQLite and PostgreSQL databases only.")

    if url.drivername.startswith("sqlite") and url.database in (None, "", ":memory:"):
        raise RuntimeError("The SQL agent requires a file-backed SQLite database.")

    connect_args = {"check_same_thread": False} if url.drivername.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)

    @event.listens_for(engine, "connect")
    def enforce_read_only(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        try:
            if engine.dialect.name == "sqlite":
                cursor.execute("PRAGMA query_only = ON")
            elif engine.dialect.name == "postgresql":
                cursor.execute("SET default_transaction_read_only = on")
        finally:
            cursor.close()

    return SQLDatabase(engine=engine, include_tables=list(SQL_AGENT_TABLES), sample_rows_in_table_info=2)


class SQLAgentService:
    async def answer(self, question: str) -> str:
        """Run the LangChain SQL agent against the allowlisted catalog tables."""
        from langchain.agents import create_agent
        from langchain_community.agent_toolkits import SQLDatabaseToolkit
        from langchain.tools import tool

        model = get_chat_model()
        database = await asyncio.to_thread(get_readonly_sql_database)
        tools = SQLDatabaseToolkit(db=database, llm=model).get_tools()

        @tool("sql_db_query")
        def readonly_sql_query(query: str) -> str:
            """Execute one SELECT query on products, categories, or inventory only."""
            try:
                safe_query = _validate_select(query, database.dialect)
            except ValueError as exc:
                return f"Query rejected: {exc}"
            return database.run_no_throw(safe_query, include_columns=True)

        tools = [readonly_sql_query if current.name == "sql_db_query" else current for current in tools]
        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=(
                "You answer administrator questions about the e-commerce catalog and inventory. "
                "Inspect the available tables and schemas before querying. Use only read-only "
                "SELECT queries, keep queries focused, and never expose passwords, tokens, or "
                "personal customer data. Explain when the database does not contain enough data."
            ),
        )
        result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
        messages = result.get("messages", [])
        for message in reversed(messages):
            if getattr(message, "type", None) == "ai":
                return message_text(message)
        return "I could not produce an answer from the database."
