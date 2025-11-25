import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.rag.knowledge_base import KnowledgeBase

def main():
    print("Starting Knowledge Base Ingestion...")
    print("-------------------------------------")
    
    kb = KnowledgeBase()
    
    # This triggers the ingestion process
    kb.ingest_specs()
    
    print("-------------------------------------")
    print("Ingestion Complete. Vector Database is ready.")

if __name__ == "__main__":
    main()
