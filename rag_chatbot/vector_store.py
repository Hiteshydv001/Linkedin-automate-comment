import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from retriever import load_project_documents, chunk_documents

def create_vector_store():
    """Embeds project documents & stores them in ChromaDB"""
    documents = load_project_documents()
    chunks = chunk_documents(documents)
    
    vector_db = Chroma.from_documents(
        documents=chunks, embedding=OpenAIEmbeddings()
    )
    
    return vector_db
