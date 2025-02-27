from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from query_handler import answer_query
import uvicorn

load_dotenv()
app = FastAPI()

class ChatQueryRequest(BaseModel):
    query: str

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