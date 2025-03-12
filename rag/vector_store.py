import os
from dotenv import load_dotenv
import requests
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def load_predefined_documents():
    """Load predefined project-related text files"""
    doc_files = ["readme.txt"]
    docs = []
    for file in doc_files:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                docs.append(f.read())
        else:
            print(f"File not found: {file}")
    return docs

def chunk_documents(documents, chunk_size=500):
    """Split large documents into smaller chunks for efficient vectorization"""
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=50,
        length_function=len
    )
    all_chunks = []
    for doc in documents:
        chunks = splitter.split_text(doc)
        all_chunks.extend(chunks)
        print(f"Created {len(chunks)} chunks: {[len(c) for c in chunks]}")
    return [Document(page_content=chunk) for chunk in all_chunks]

def get_gemini_embeddings(texts):
    """Fetch embeddings from Gemini API for the provided texts"""
    headers = {
        "Content-Type": "application/json"
    }
    url = f"https://generativelanguage.googleapis.com/v1/models/text-embedding-004:embedContent?key={GEMINI_API_KEY}"
    embeddings = []
    
    for text in texts:
        data = {
            "content": {
                "parts": [{"text": text}]
            }
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            embedding = response.json()["embedding"]["values"]
            embeddings.append(embedding)
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")
    
    return embeddings

class GeminiEmbeddingFunction:
    """Custom embedding function for Chroma"""
    def __init__(self, api_key):
        self.api_key = api_key

    def embed_documents(self, texts):
        """Embed a list of documents"""
        return get_gemini_embeddings(texts)

    def embed_query(self, text):
        """Embed a single query string"""
        return get_gemini_embeddings([text])[0]

def create_vector_store():
    """Creates and stores vector embeddings in ChromaDB using predefined documents"""
    try:
        documents = load_predefined_documents()
        if not documents:
            raise ValueError("No documents found to process.")

        chunks = chunk_documents(documents)
        if not chunks:
            raise ValueError("No chunks created.")

        embedding_function = GeminiEmbeddingFunction(GEMINI_API_KEY)
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_function,
            persist_directory="./chroma_db"
        )
        return vector_db
    except Exception as e:
        print(f"Error while creating vector store: {str(e)}")
        return None

if __name__ == "__main__":
    vector_db = create_vector_store()
    if vector_db:
        print("Vector store created and saved successfully!")
    else:
        print("Failed to create vector store.")