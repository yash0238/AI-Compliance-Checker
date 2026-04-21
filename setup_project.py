import os
import shutil
from pathlib import Path

def setup_directories():
    """Create necessary data directories if they don't exist."""
    dirs = [
        "data/raw",
        "data/processed",
        "data/chroma_db",
        "data/hf_cache",
        "data/knowledge_base"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Directory ready: {d}")

def setup_env():
    """Create .env from .env.example if it doesn't exist."""
    if not os.path.exists(".env"):
        shutil.copy(".env.example", ".env")
        print("Created .env from .env.example. PLEASE UPDATE YOUR API KEYS!")
    else:
        print(".env already exists.")

def download_models():
    """Pre-download embedding models to the local cache."""
    print("Pre-downloading embedding model (all-MiniLM-L6-v2)...")
    try:
        # Set cache directories to match project structure
        os.environ["HF_HOME"] = os.path.join(os.getcwd(), "data", "hf_cache")
        os.environ["TRANSFORMERS_CACHE"] = os.path.join(os.getcwd(), "data", "hf_cache")
        
        from langchain_huggingface import HuggingFaceEmbeddings
        
        model_name = "all-MiniLM-L6-v2"
        _ = HuggingFaceEmbeddings(model_name=model_name)
        print(f"Model {model_name} downloaded successfully to data/hf_cache.")
    except ImportError:
        print("Error: langchain-huggingface or sentence-transformers not installed.")
        print("Please run: pip install langchain-huggingface sentence-transformers")
    except Exception as e:
        print(f"An error occurred during model download: {e}")

if __name__ == "__main__":
    print("=== AI Compliance Checker Setup ===")
    setup_directories()
    setup_env()
    download_models()
    print("====================================")
    print("Setup complete. Remember to add your API keys to the .env file.")
