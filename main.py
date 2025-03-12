from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uvicorn
from typing import List

from rag.query_handler import answer_query


# Assuming agents.py exists in your project
from agents import AgentManager

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Enable CORS (adjust allow_origins for production security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent manager (assumes agents.py exists)
agent_manager = AgentManager()

# Request Models
class SummarizeRequest(BaseModel):
    text: str

class WritePostRequest(BaseModel):
    topic: str
    outline: str = ""

class SanitizeDataRequest(BaseModel):
    data: str

class RefinePostRequest(BaseModel):
    draft: str

class ValidatePostRequest(BaseModel):
    topic: str
    article: str

class GenerateCommentRequest(BaseModel):
    post_content: str

class SentimentAnalysisRequest(BaseModel):
    text: str

class ChatQueryRequest(BaseModel):
    query: str

# Health Check Route
@app.get("/")
def home():
    return {"message": "LinkedIn Automation API is running!"}

# API Routes for LinkedIn Automation Features
@app.post("/summarize")
def summarize(request: SummarizeRequest):
    try:
        summary = agent_manager.get_agent("summarize").execute(request.text)
        validation_agent = agent_manager.get_agent("summarize_validator")
        validation = validation_agent.execute(request.text, summary) if validation_agent else "Validation agent not found"
        return {"summary": summary, "validation": validation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/write_post")
def write_post(request: WritePostRequest):
    try:
        post = agent_manager.get_agent("write_post").execute(request.topic, request.outline)
        validation = agent_manager.get_agent("write_post_validator").execute(request.topic, post)
        return {"post": post, "validation": validation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sanitize_data")
def sanitize_data(request: SanitizeDataRequest):
    try:
        sanitized_data = agent_manager.get_agent("sanitize_data").execute(request.data)
        validation = agent_manager.get_agent("sanitize_data_validator").execute(request.data, sanitized_data)
        return {"sanitized_data": sanitized_data, "validation": validation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refine_post")
def refine_post(request: RefinePostRequest):
    try:
        refined_post = agent_manager.get_agent("refiner").execute(request.draft)
        return {"refined_post": refined_post}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate_post")
def validate_post(request: ValidatePostRequest):
    try:
        validation = agent_manager.get_agent("validator").execute(request.topic, request.article)
        return {"validation": validation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_comments")
def generate_comments(request: GenerateCommentRequest):
    try:
        comments = agent_manager.get_agent("generate_comment").execute(request.post_content)
        if not isinstance(comments, list):
            comments = [comments]
        return {"comments": comments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comments: {str(e)}")

@app.post("/sentiment_analysis")
def sentiment_analysis(request: SentimentAnalysisRequest):
    try:
        sentiment = agent_manager.get_agent("sentiment_analysis").execute(request.text)
        return {"sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# RAG Chatbot Route
@app.post("/rag_chat")
def rag_chat(request: ChatQueryRequest):
    try:
        response = answer_query(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Server starting on http://0.0.0.0:{port} ...")
    uvicorn.run(app, host="0.0.0.0", port=port)