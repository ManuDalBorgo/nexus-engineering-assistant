import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

# Define persistence directory
DB_DIR = os.path.join(os.path.dirname(__file__), "../../data/chroma_db")
SPECS_DIR = os.path.join(os.path.dirname(__file__), "../../data/specs")

class KnowledgeBase:
    def __init__(self):
        self.vector_store = None
        # Use Local Embeddings to avoid API Key issues
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def ingest_specs(self):
        """Reads spec files and indexes them into ChromaDB."""
        if not os.path.exists(SPECS_DIR):
            print(f"No specs directory found at {SPECS_DIR}")
            return

        documents = []
        for filename in os.listdir(SPECS_DIR):
            if filename.endswith(".txt"):
                file_path = os.path.join(SPECS_DIR, filename)
                loader = TextLoader(file_path)
                documents.extend(loader.load())

        if not documents:
            print("No documents found to ingest.")
            return

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)

        print(f"Ingesting {len(docs)} chunks into VectorDB...")
        self.vector_store = Chroma.from_documents(
            documents=docs, 
            embedding=self.embeddings, 
            persist_directory=DB_DIR
        )
        print("Ingestion complete.")

    def get_retriever(self):
        if not self.vector_store:
            # Load existing DB
            if os.path.exists(DB_DIR):
                self.vector_store = Chroma(
                    persist_directory=DB_DIR, 
                    embedding_function=self.embeddings
                )
            else:
                # If DB doesn't exist, try to ingest
                self.ingest_specs()
        
        return self.vector_store.as_retriever()

if __name__ == "__main__":
    # For testing
    kb = KnowledgeBase()
    kb.ingest_specs()
