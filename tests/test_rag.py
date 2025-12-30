import os
import sys
import shutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.rag.knowledge_base import KnowledgeBase, DB_DIR

def test_rag_ingestion():
    print("Testing RAG Ingestion...")
    
    # Clean up existing DB for a fresh test
    if os.path.exists(DB_DIR):
        print(f"Cleaning up existing DB at {DB_DIR}")
        shutil.rmtree(DB_DIR)
    
    kb = KnowledgeBase()
    kb.ingest_specs()
    
    retriever = kb.get_retriever()
    query = "AXI handshake"
    docs = retriever.get_relevant_documents(query)
    
    print(f"Query: {query}")
    print(f"Number of documents retrieved: {len(docs)}")
    
    if len(docs) > 0:
        print("✅ Success: Documents retrieved.")
        for i, doc in enumerate(docs[:2]):
            print(f"\nDocument {i+1} snippet:")
            print(doc.page_content[:200] + "...")
    else:
        print("❌ Failure: No documents retrieved.")

if __name__ == "__main__":
    # Ensure specs directory exists and has content for testing
    specs_dir = os.path.join(os.path.dirname(__file__), "../backend/data/specs")
    if not os.path.exists(specs_dir):
        os.makedirs(specs_dir)
        with open(os.path.join(specs_dir, "test_spec.txt"), "w") as f:
            f.write("The AXI handshake process involves the VALID and READY signals. " * 50)
    
    test_rag_ingestion()
