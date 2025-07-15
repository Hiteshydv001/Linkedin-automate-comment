from qdrant_client import QdrantClient
import pandas as pd

client = QdrantClient(host="localhost", port=6333)

def save_embeddings(df: pd.DataFrame, collection_name: str = "charts"):
    pass

def retrieve_data(query: str):
    return None