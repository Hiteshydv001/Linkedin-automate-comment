import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai

# Load API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# FAISS Storage Path
VECTOR_STORE_PATH = "faiss_index"

def initialize_vector_store():
    """Ensures FAISS index is initialized with useful context data."""
    if not os.path.exists(VECTOR_STORE_PATH):
        print("📂 Vector store not found. Initializing with base data...")
        sample_text = [
            "LinkedIn is a professional network where users engage in discussions.",
            "Effective LinkedIn comments are short, relevant, and engaging.",
            "Networking on LinkedIn involves thoughtful engagement with posts.",
            "Good comments on LinkedIn add value without being too generic."
        ]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        text_chunks = text_splitter.split_text("\n".join(sample_text))

        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local(VECTOR_STORE_PATH)

def get_conversational_chain():
    """Creates an AI model to generate relevant comments."""
    prompt_template = """
    You are a LinkedIn comment generator. Your response should be:

    - Directly related to the content of the post.
    - Short and concise (1-2 sentences max).
    - If unsure, respond with: "Nice post! 👍".

    Context:\n {context}\n
    Post Content: \n{question}\n

    Comment:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

def generate_comment(post_content):
    """Generates a comment for LinkedIn post content."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Load FAISS index
    new_db = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(post_content)

    print(f"🔍 Retrieved {len(docs)} relevant docs for context.")

    # Generate response
    chain = get_conversational_chain()
    
    for attempt in range(3):  # Retry up to 3 times
        print(f"⏳ Attempt {attempt + 1}: Generating comment...")
        response = chain.invoke({"input_documents": docs, "question": post_content})
        
        comment_text = response["output_text"].strip()
        print(f"📝 AI Generated Comment: {comment_text}")

        if comment_text and comment_text not in ["👍", "Great post!", "Nice!", ""]:
            return comment_text  # Return valid comment

        print("⚠️ AI generated an empty or generic response. Retrying...")

    return "Nice post! 👍"  # Default fallback comment

# Initialize FAISS index if missing
initialize_vector_store()


def get_llm_response(prompt):
    """Generates a response using Gemini API"""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    return response.text