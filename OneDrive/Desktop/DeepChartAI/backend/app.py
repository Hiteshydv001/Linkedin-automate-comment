# backend/app.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from routes import generate_chart, analyze_trends
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Chart Builder")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )

@app.post("/generate-chart/")
async def create_chart(
    query: str = Form(...),
    chart_type: str = Form(default=None),
    file: UploadFile = File(default=None),
    json_data: str = Form(default=None),
    manual_data: str = Form(default=None)
):
    try:
        if file:
            if not file.filename.endswith(".csv"):
                raise HTTPException(status_code=400, detail="Only CSV files are supported")
            content = await file.read()
        elif json_data:
            content = json_data.encode('utf-8')
        elif manual_data:
            content = manual_data.encode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="No data provided")
        
        response = generate_chart(query, content, chart_type)
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.post("/analyze-trends/")
async def get_trends(query: str = Form(...), file: UploadFile = File(default=None)):
    try:
        if file and file.filename.endswith(".csv"):
            content = await file.read()
        else:
            raise HTTPException(status_code=400, detail="CSV file required for trend analysis")
        
        response = analyze_trends(query, content)
        return response
    except Exception as e:
        logger.error(f"Error analyzing trends: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)