import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import shutil

# Load environment variables
load_dotenv()

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    if os.path.exists("faiss_index"):
        shutil.rmtree("faiss_index")

    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    You are a comment generator trained to generate **very short**, relevant, and context-sensitive comments based on LinkedIn post content. Your response should be:

    - Directly related to the content of the post.
    - Brief and concise (aim for no more than 1-2 sentences).

    If you are unable to generate an appropriate comment based on the provided context, reply with only a **thumbs-up emoji (👍)**.

    Context:\n {context}\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

def user_input(user_question, post_text):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    text_chunks = get_text_chunks(post_text)
    get_vector_store(text_chunks)

    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    return response["output_text"]

def main(post_texts):
    print("Processing LinkedIn Posts...")

    if not post_texts:
        print("No posts found. Exiting.")
        return

    for idx, post_text in enumerate(post_texts):
        print(f"Generating comment for Post {idx + 1}...")
        comment = user_input("Generate a very short comment for this LinkedIn post.", post_text)
        print(f"Post {idx + 1} Comment: {comment}")

if __name__ == "__main__":
    from webscrapper import scrape_linkedin_posts  # Import function from webscrapper.py

    post_texts = scrape_linkedin_posts(os.getenv("EMAIL"), os.getenv("PASSWORD"))
    main(post_texts)
