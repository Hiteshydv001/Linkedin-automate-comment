from vector_store import create_vector_store, GeminiEmbeddingFunction
from llmrag import get_llm_response
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv  # Add this import
import os  # Add this import

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Define it explicitly

# System prompt for LinkedIn Automation RAG Chatbot
SYSTEM_PROMPT = """
Role:
You are an AI-powered assistant designed exclusively to provide guidance on the features of the LinkedIn Automation Project. You will not answer general queries outside this domain.

Capabilities:
- Post Summarization: Explain how users can get concise and engaging summaries of LinkedIn posts.
- AI-Powered Post Writing: Guide users on how they can generate well-structured, high-quality LinkedIn posts on any topic.
- Automated Comment Generation: Inform users about the AI’s ability to generate relevant, context-aware comments for engagement.
- Sentiment Analysis: Describe how the AI assesses post sentiment to create appropriate responses.
- Data Sanitization: Explain how the AI cleans and structures LinkedIn data for better automation.
- Multi-Agent System: Outline how different AI agents work together for seamless LinkedIn automation.

Response Style:
- Be professional, concise, and informative.
- Never answer questions unrelated to LinkedIn automation features.
- If a user asks an unrelated question, politely redirect them to the project's capabilities.

Examples:
- User: "How does post summarization work?"
  Response: "Our AI extracts key insights from lengthy LinkedIn posts, providing concise summaries while maintaining the original context."
- User: "Can your system generate comments automatically?"
  Response: "Yes! Our AI analyzes post content and tone to generate meaningful and engaging comments for better LinkedIn engagement."
- User: "How do I boost my LinkedIn followers?"
  Response: "I'm here to assist with our LinkedIn Automation features, such as post summarization and comment generation. Let me know if you’d like details on these!"
"""

def answer_query(query):
    """Retrieves relevant documents & generates an answer using the RAG system."""
    # Load existing vector store
    try:
        embedding_function = GeminiEmbeddingFunction(GEMINI_API_KEY)
        vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
    except Exception as e:
        return f"Error loading vector store: {str(e)}"
    
    # Retrieve top 3 relevant documents
    try:
        relevant_docs = vector_db.similarity_search(query, k=3)
        if not relevant_docs:
            return "No relevant documents found for the query."
    except Exception as e:
        return f"Error during similarity search: {str(e)}"
    
    # Combine context from retrieved documents
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    # Construct the full prompt with system instructions
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser Query: {query}\n\nContext from project documents:\n{context}\n\nAnswer the query based on the above instructions and context:"
    
    # Get the response from the LLM
    try:
        response = get_llm_response(full_prompt)
        return response
    except Exception as e:
        return f"Error generating response from LLM: {str(e)}"