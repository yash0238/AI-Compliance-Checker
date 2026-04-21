import os

# Force local HuggingFace cache to avoid Windows permission errors
os.environ["HF_HOME"] = os.path.join(os.getcwd(), "data", "hf_cache")
os.environ["TRANSFORMERS_CACHE"] = os.path.join(os.getcwd(), "data", "hf_cache")

import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Configuration
CHROMA_DB_DIR = os.path.join("data", "chroma_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2" # Lightweight, fast model

class VectorStoreManager:
    def __init__(self, collection_name="indian_law_kb"):
        self.collection_name = collection_name
        self.persist_directory = CHROMA_DB_DIR
        
        # Ensure the directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize embeddings (HuggingFace sentence-transformers)
        print(f"Loading embedding model: {EMBEDDING_MODEL}...")
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        # Initialize Chroma vector store with Langchain wrapper
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        print(f"Vector Store initialized. Existing documents: {self.vector_store._collection.count()}")

    def get_retriever(self, k=3):
        """Returns a configured retriever object for use in chains."""
        return self.vector_store.as_retriever(search_kwargs={"k": k})

    def search_similar(self, query: str, k=3):
        """Perform a simple similarity search on the vector db."""
        results = self.vector_store.similarity_search(query, k=k)
        return results

    def add_documents(self, chunks):
        """Adds LangChain Document chunks to the vector store."""
        print(f"Adding {len(chunks)} chunks to Vector Store...")
        self.vector_store.add_documents(chunks)
        print("Documents added and persisted.")

if __name__ == "__main__":
    # Test initialization
    manager = VectorStoreManager()
