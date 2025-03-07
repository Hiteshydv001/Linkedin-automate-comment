from vector_store import create_vector_store
from llm import get_llm_response

def answer_query(query):
    """Retrieves relevant docs & generates an answer"""
    vector_db = create_vector_store()
    relevant_docs = vector_db.similarity_search(query, k=3)  # Retrieve top 3 docs
    
    context = "\n".join([doc.page_content for doc in relevant_docs])
    prompt = f"Based on the project documents, answer the following:\n{query}\n\nContext:\n{context}"
    
    return get_llm_response(prompt)
