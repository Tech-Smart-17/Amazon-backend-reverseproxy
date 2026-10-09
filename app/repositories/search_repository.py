"""Product semantic search repository backed by LangChain and Chroma."""
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.services.langchain_runtime import get_vector_store


class SearchRepository:
    def __init__(self):
        # A versioned collection keeps historic 64-dimensional vectors untouched.
        self._vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.LANGCHAIN_CHUNK_SIZE,
            chunk_overlap=settings.LANGCHAIN_CHUNK_OVERLAP,
        )

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = get_vector_store("products_langchain_v1")
        return self._vector_store

    def index_product(
        self, product_id: str, title: str, description: str, brand: str, category: str
    ) -> None:
        """Split and index a product, replacing all previously indexed chunks."""
        self.delete_product(product_id)
        text_content = "\n".join(
            value.strip()
            for value in (title, description or "", brand or "", category or "")
            if value and value.strip()
        )
        document = Document(
            page_content=text_content,
            metadata={
                "product_id": product_id,
                "title": title,
                "brand": brand or "",
                "category": category or "",
                "source_type": "product",
            },
        )
        chunks = self.text_splitter.split_documents([document])
        ids = [f"{product_id}:{index}" for index in range(len(chunks))]
        if chunks:
            self.vector_store.add_documents(chunks, ids=ids)

    def delete_product(self, product_id: str) -> None:
        """Remove every stored chunk that belongs to a product."""
        existing = self.vector_store.get(where={"product_id": product_id})
        ids = existing.get("ids", []) if existing else []
        if ids:
            self.vector_store.delete(ids=ids)

    def search_semantic(self, query: str, limit: int = 10) -> List[str]:
        """Return distinct product ids ranked by semantic similarity."""
        if not query.strip():
            return []
        documents = self.vector_store.similarity_search(
            query,
            k=max(limit * 3, limit),
            filter={"source_type": "product"},
        )
        product_ids = []
        seen = set()
        for document in documents:
            product_id = document.metadata.get("product_id")
            if product_id and product_id not in seen:
                seen.add(product_id)
                product_ids.append(product_id)
                if len(product_ids) == limit:
                    break
        return product_ids

    def get_similar_products(self, product_id: str, limit: int = 5) -> List[str]:
        """Find other products nearest to the indexed product's text."""
        existing = self.vector_store.get(
            where={"product_id": product_id},
            include=["documents"],
        )
        documents = existing.get("documents", []) if existing else []
        if not documents or not documents[0]:
            return []
        matches = self.vector_store.similarity_search(
            documents[0],
            k=max(limit * 3 + 1, limit + 1),
            filter={"source_type": "product"},
        )
        product_ids = []
        seen = {product_id}
        for document in matches:
            match_id = document.metadata.get("product_id")
            if match_id and match_id not in seen:
                seen.add(match_id)
                product_ids.append(match_id)
                if len(product_ids) == limit:
                    break
        return product_ids
