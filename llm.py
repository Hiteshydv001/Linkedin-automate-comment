import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv
import shutil
from google.generativeai import generate_content


# Load environment variables and set up Google API
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Path to the PDF file
pdf_path = r"C:\Users\Asus\OneDrive\Desktop\linkedin automation\linkedin_posts_report.pdf"

# Hardcoded question to generate a comment
hardcoded_question = "Generate a very short comment for this LinkedIn post."


def generate_comment(post_text):
    """Generate a LinkedIn comment using the Gemini API."""
    prompt = f"Generate a professional yet engaging comment for the following LinkedIn post:\n\n{post_text}"
    response = generate_content(prompt)
    return response.text if response else "Could not generate a comment."

# Function to extract text from the PDF
def get_pdf_text(pdf_path):
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to split the text into chunks for better processing
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

# Function to save vector store (FAISS index)
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Remove the old FAISS index if it exists
    if os.path.exists("faiss_index"):
        shutil.rmtree("faiss_index")
    
    # Create a new FAISS index and save it
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# Function to create a conversational chain for question answering
def get_conversational_chain():
    prompt_template = """
    You are a comment generator trained to generate **very short**, relevant, and context-sensitive comments based on LinkedIn post content. Your response should be:
    
    - Directly related to the content of the post.
    - Brief and concise (aim for no more than 1-2 sentences).
    
    If you are unable to generate an appropriate comment based on the provided context, reply with only a **thumbs-up emoji (👍)**. Do not provide any incorrect or off-topic responses.
    
    Context:\n {context}\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

# Function to process user input and generate a response
def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Load the FAISS index, allowing dangerous deserialization (only for trusted files)
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    # Print the docs to verify the context
    print("Retrieved documents for context: ", docs)
    
    chain = get_conversational_chain()

    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    
    return response["output_text"]

# Main function to orchestrate the process
def main():
    print("Processing PDFs...")
    
    # Extract text from PDF and print for debugging
    raw_text = get_pdf_text(pdf_path)
    print("Extracted Text from PDF: ", raw_text)
    
    # Generate text chunks and print the number of chunks for debugging
    text_chunks = get_text_chunks(raw_text)
    print(f"Generated {len(text_chunks)} chunks of text.")
    
    # Generate the FAISS index (and update it)
    get_vector_store(text_chunks)
    
    print("PDF Processing Complete. You can now ask questions.")
    
    # Hardcoded question to generate a comment
    print("Generating a short comment for the LinkedIn post...")
    comment = user_input(hardcoded_question)
    
    print("Generated Comment: ", comment)

if __name__ == "__main__":
    main()