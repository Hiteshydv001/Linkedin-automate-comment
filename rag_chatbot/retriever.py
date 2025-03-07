from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
import os

def load_project_documents():
    """Loads all project-related text files"""
    doc_files = ["data/readme.txt"]
    docs = []
    
    for file in doc_files:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                docs.append(f.read())

    return docs

def chunk_documents(documents, chunk_size=500):
    """Splits large documents into smaller chunks"""
    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)
    return splitter.split_documents(documents)

