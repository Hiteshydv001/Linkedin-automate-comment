from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents import AgentManager

app = FastAPI()

# ✅ Enable CORS for all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_manager = AgentManager()

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

@app.get("/")
def home():
    return {"message": "LinkedIn Automation API is running!"}

@app.post("/summarize")
def summarize(request: SummarizeRequest):
    summary = agent_manager.get_agent("summarize").execute(request.text)
    validation_agent = agent_manager.get_agent("summarize_validator")
    validation = validation_agent.execute(request.text, summary) if validation_agent else "Validation agent not found"
    return {"summary": summary, "validation": validation}

@app.post("/write_post")
def write_post(request: WritePostRequest):
    post = agent_manager.get_agent("write_post").execute(request.topic, request.outline)
    validation = agent_manager.get_agent("write_post_validator").execute(request.topic, post)
    return {"post": post, "validation": validation}

@app.post("/sanitize_data")
def sanitize_data(request: SanitizeDataRequest):
    sanitized_data = agent_manager.get_agent("sanitize_data").execute(request.data)
    validation = agent_manager.get_agent("sanitize_data_validator").execute(request.data, sanitized_data)
    return {"sanitized_data": sanitized_data, "validation": validation}

@app.post("/refine_post")
def refine_post(request: RefinePostRequest):
    refined_post = agent_manager.get_agent("refiner").execute(request.draft)
    return {"refined_post": refined_post}

@app.post("/validate_post")
def validate_post(request: ValidatePostRequest):
    validation = agent_manager.get_agent("validator").execute(request.topic, request.article)
    return {"validation": validation}

@app.post("/generate_comment")
def generate_comment(request: GenerateCommentRequest):
    comment = agent_manager.get_agent("generate_comment").execute(request.post_content)
    return {"comment": comment}

@app.post("/sentiment_analysis")
def sentiment_analysis(request: SentimentAnalysisRequest):
    sentiment = agent_manager.get_agent("sentiment_analysis").execute(request.text)
    return {"sentiment": sentiment}
