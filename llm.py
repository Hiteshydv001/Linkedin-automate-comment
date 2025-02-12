import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to generate a comment based on LinkedIn post text
def generate_comment(post_text):
    if not post_text.strip():
        return "👍"  # Return thumbs-up emoji if post is empty

    # Define the prompt template
    prompt_template = """
    You are a comment generator trained to generate **very short**, relevant, and context-sensitive comments based on LinkedIn post content. Your response should be:
    
    - Directly related to the content of the post.
    - Brief and concise (1-2 sentences).
    
    If you are unable to generate an appropriate comment, reply with **only a thumbs-up emoji (👍)**.

    Context: {context}
    Question: Generate a very short comment for this LinkedIn post.

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    # Generate response
    response = chain({"context": post_text}, return_only_outputs=True)

    return response.get("output_text", "👍")  # Return generated comment or thumbs-up emoji

# Only run if executed directly
if __name__ == "__main__":
    sample_post = "Excited to share my latest blog post on AI in finance!"
    print("Generated Comment:", generate_comment(sample_post))
