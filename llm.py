import os
<<<<<<< HEAD
import shutil
import google.generativeai as genai
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.document_loaders import TextLoader
from PyPDF2 import PdfReader

# ✅ Load API Key Securely
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("ERROR: GOOGLE_API_KEY not found. Check your .env file.")
genai.configure(api_key=api_key)

# ✅ Set PDF Path
PDF_PATH = r"D:/JWoC 2k25/linkedin-automate-comment/linkedin_comments_report.pdf"
FAISS_INDEX_PATH = "faiss_index"

# ✅ Extract Text from PDF
def extract_pdf_text(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    return text.strip()

# ✅ Split Text into Chunks
def split_text_chunks(text):
    """Splits text into smaller chunks for better embedding processing."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=500)  
    return text_splitter.split_text(text)

# ✅ Create or Update FAISS Index
def create_faiss_index(text_chunks):
    """Creates or updates the FAISS index with new data."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Remove old index if exists
    if os.path.exists(FAISS_INDEX_PATH):
        shutil.rmtree(FAISS_INDEX_PATH)

    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local(FAISS_INDEX_PATH)

# ✅ Conversational Chain Setup
def get_conversational_chain():
    """Sets up a conversational AI chain for generating responses."""
    prompt_template = """
    You are an AI trained to generate **concise and engaging LinkedIn comments**. Your response should:

    - Be **short** (1-2 sentences).
    - Stay **contextually relevant**.
    - Be **positive and engaging**.
    - Avoid generic responses like '👍' or 'Great post!'

    If no relevant comment can be generated, **DO NOT** reply with 'Could you clarify your post topic?'. Instead, provide a general comment about LinkedIn engagement.
=======
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
>>>>>>> main

    Context:\n {context}\n
    Post Content: \n{question}\n

    Comment:
    """
<<<<<<< HEAD

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.5)  
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

# ✅ Retrieve Context and Generate Response
def generate_contextual_comment(user_question):
    """Retrieves context from FAISS and generates a response."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Load FAISS index
    new_db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    # **Debugging: Print retrieved documents**
    if not docs:
        print("⚠️ No relevant documents found in FAISS index.")
        return "LinkedIn is a great platform for networking and sharing ideas. Keep posting!"

    print(f"📌 Retrieved {len(docs)} related documents for context.")
    for idx, doc in enumerate(docs):
        print(f"🔍 Context {idx+1}: {doc.page_content[:200]}...")  

    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    return response["output_text"] if response and response["output_text"].strip() else "Networking is key on LinkedIn! Keep engaging with your audience."

# ✅ Main Process
def main():
    print("🚀 Processing PDF...")
    
    # Extract and process text
    raw_text = extract_pdf_text(PDF_PATH)
    if not raw_text:
        print("⚠️ No text extracted from the PDF.")
        return

    print(f"📜 Extracted {len(raw_text)} characters from PDF.")
    
    text_chunks = split_text_chunks(raw_text)
    print(f"🔗 Created {len(text_chunks)} text chunks.")

    # Generate FAISS index
    create_faiss_index(text_chunks)
    print("✅ FAISS index updated.")

    # Generate LinkedIn comment
    print("\n💬 Generating LinkedIn comment...")
    comment = generate_contextual_comment("Generate a short LinkedIn comment for this post.")
    
    print("\n✨ Generated Comment: ", comment)

# ✅ Run the script
if __name__ == "__main__":
    main()
=======
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
>>>>>>> main
