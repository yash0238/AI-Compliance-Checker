from src.rag.vector_store import VectorStoreManager

def test_rag_retrieval():
    print("Testing Vector DB Retrieval...\n")
    try:
        # Initialize the vector store manager
        vsm = VectorStoreManager()
        
        # Test query designed to hit generic legal context
        query = "What does the constitution say about the Right to Equality?"
        print(f"Query: '{query}'\n")
        
        results = vsm.search_similar(query, k=2)
        
        if not results:
            print("No results found. (This is expected if knowledge_base is empty).")
            print("Please add PDF documents to data/knowledge_base/ and run ingestion_engine.py")
        else:
            print("Results Retrieved:")
            for i, res in enumerate(results, 1):
                print(f"\n--- Result {i} ---")
                print(f"Source: {res.metadata.get('source', 'Unknown')}")
                # Print a snippet of the text
                snippet = res.page_content.replace('\n', ' ')
                print(f"Content Preview: {snippet[:200]}...")

    except Exception as e:
        print(f"Error during retrieval: {e}")

if __name__ == "__main__":
    test_rag_retrieval()
