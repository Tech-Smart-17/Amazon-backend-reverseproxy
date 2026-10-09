"""Multi-database manager for async SQL, MongoDB, and Redis services."""
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import motor.motor_asyncio
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger("amazon_backend")

# ==========================================
# 1. SQL DATABASE (SQLAlchemy 2.0 Async)
# ==========================================
Base = declarative_base()

# Handle SQLite vs PostgreSQL async drivers gracefully
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")

connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing Async SQL Session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ==========================================
# 2. MONGODB (Motor Async + Resilient In-Memory Mock Fallback)
# ==========================================
class ResilientMongoCollection:
    def __init__(self, name: str):
        self.name = name
        self._data = {}

    async def insert_one(self, document: dict):
        doc_id = document.get("_id", str(len(self._data) + 1))
        document["_id"] = str(doc_id)
        self._data[str(doc_id)] = document
        class Result:
            inserted_id = str(doc_id)
        return Result()

    async def find_one(self, query: dict):
        for doc in self._data.values():
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc.copy()
        return None

    def find(self, query: dict = None):
        query = query or {}
        results = []
        for doc in self._data.values():
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                results.append(doc.copy())
        
        class Cursor:
            def __init__(self, items):
                self.items = items
            def sort(self, key, direction=1):
                return self
            def limit(self, n):
                self.items = self.items[:n]
                return self
            async def to_list(self, length=100):
                return self.items[:length]
            def __aiter__(self):
                self._iter = iter(self.items)
                return self
            async def __anext__(self):
                try:
                    return next(self._iter)
                except StopIteration:
                    raise StopAsyncIteration
        return Cursor(results)

    async def update_one(self, query: dict, update: dict, upsert: bool = False):
        existing = await self.find_one(query)
        if existing:
            doc_id = str(existing["_id"])
            if "$set" in update:
                self._data[doc_id].update(update["$set"])
            if "$push" in update:
                for k, v in update["$push"].items():
                    if k not in self._data[doc_id] or not isinstance(self._data[doc_id][k], list):
                        self._data[doc_id][k] = []
                    self._data[doc_id][k].append(v)
            if "$pull" in update:
                for k, v in update["$pull"].items():
                    if k in self._data[doc_id] and isinstance(self._data[doc_id][k], list):
                        self._data[doc_id][k] = [x for x in self._data[doc_id][k] if x != v]
            class Result:
                modified_count = 1
            return Result()
        elif upsert:
            new_doc = query.copy()
            if "$set" in update:
                new_doc.update(update["$set"])
            await self.insert_one(new_doc)
            class Result:
                modified_count = 1
            return Result()
        class Result:
            modified_count = 0
        return Result()

    async def delete_one(self, query: dict):
        existing = await self.find_one(query)
        if existing:
            del self._data[str(existing["_id"])]
            class Result:
                deleted_count = 1
            return Result()
        class Result:
            deleted_count = 0
        return Result()

    async def delete_many(self, query: dict):
        to_del = []
        for k_id, doc in self._data.items():
            match = True
            for qk, qv in query.items():
                if doc.get(qk) != qv:
                    match = False
                    break
            if match:
                to_del.append(k_id)
        for d in to_del:
            del self._data[d]
        class Result:
            deleted_count = len(to_del)
        return Result()

class ResilientMongoDB:
    def __init__(self):
        self.collections = {}

    def get_collection(self, name: str):
        if name not in self.collections:
            self.collections[name] = ResilientMongoCollection(name)
        return self.collections[name]

    def __getitem__(self, name: str):
        return self.get_collection(name)

mongo_client = None
mongo_db = None

def init_mongo():
    global mongo_client, mongo_db
    try:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=1000
        )
        mongo_db = mongo_client[settings.MONGODB_DB_NAME]
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. Using resilient in-memory MongoDB mock.")
        mongo_db = ResilientMongoDB()

init_mongo()

def get_mongo_db():
    return mongo_db


# ==========================================
# 3. REDIS (Async Redis + Resilient In-Memory Cache)
# ==========================================
class ResilientRedisCache:
    def __init__(self):
        self.store = {}

    async def get(self, key: str):
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int = None):
        self.store[key] = value
        return True

    async def delete(self, key: str):
        return self.store.pop(key, None) is not None

    async def incr(self, key: str):
        val = int(self.store.get(key, 0)) + 1
        self.store[key] = str(val)
        return val

    async def expire(self, key: str, seconds: int):
        return True

    async def ping(self):
        return True

redis_client = None

async def init_redis():
    global redis_client
    try:
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await r.ping()
        redis_client = r
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Using resilient in-memory Redis cache.")
        redis_client = ResilientRedisCache()

def get_redis():
    if redis_client is None:
        return ResilientRedisCache()
    return redis_client

