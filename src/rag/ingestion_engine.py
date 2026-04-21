import os
import glob

# Force local HuggingFace cache to avoid Windows permission errors
os.environ["HF_HOME"] = os.path.join(os.getcwd(), "data", "hf_cache")
os.environ["TRANSFORMERS_CACHE"] = os.path.join(os.getcwd(), "data", "hf_cache")

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.rag.vector_store import VectorStoreManager

KNOWLEDGE_BASE_DIR = os.path.join("data", "knowledge_base")

def ingest_pdfs():
    """Loads all PDFs from the knowledge base directory and indexes them."""
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        print(f"Error: {KNOWLEDGE_BASE_DIR} does not exist.")
        return

    pdf_files = glob.glob(os.path.join(KNOWLEDGE_BASE_DIR, "*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {KNOWLEDGE_BASE_DIR}.")
        return

    all_docs = []
    
    print(f"Found {len(pdf_files)} PDF files to ingest.")
    for file_path in pdf_files:
        print(f"Loading {os.path.basename(file_path)}...")
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            all_docs.extend(docs)
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")

    if not all_docs:
        print("No document content could be extracted.")
        return

    # Split documents into semantic chunks
    print(f"Splitting {len(all_docs)} pages into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(all_docs)
    
    print(f"Created {len(chunks)} text chunks.")

    # Ingest into Vector Store
    vsm = VectorStoreManager()
    vsm.add_documents(chunks)
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest_pdfs()
