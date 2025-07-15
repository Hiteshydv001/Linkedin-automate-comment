# backend/llm_integration.py
import google.generativeai as genai
import json
import pandas as pd
from config import Config
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=Config.LLM_API_KEY)
model = genai.GenerativeModel('gemini-pro')

CHART_PROMPT = """
Given a user query '{query}' and available dataset columns {columns}, suggest a chart type (line, bar, pie, scatter, heatmap) and the X and Y axis labels based on common data visualization practices. Respond in JSON format with the keys: "chart_type", "x", and "y". Ensure "x" and "y" are chosen from the provided columns. For example:
- Query: "Show me sales trends over time", Columns: ["Date", "Sales"] -> {"chart_type": "line", "x": "Date", "y": "Sales"}
- Query: "Compare product sales", Columns: ["Product", "Sales"] -> {"chart_type": "bar", "x": "Product", "y": "Sales"}
- Query: "Distribution of categories", Columns: ["Category", "Count"] -> {"chart_type": "pie", "x": "Category", "y": "Count"}
- Query: "Heatmap of sales by region", Columns: ["Region", "Sales"] -> {"chart_type": "heatmap", "x": "Region", "y": "Sales"}
"""

TREND_PROMPT = """
Given a user query '{query}' and a dataset with columns {columns}, analyze the data and provide insights or trends in plain text. For example:
- Query: "What are the sales trends?", Columns: ["Date", "Sales"] -> "Sales have increased steadily from January to April 2023."
"""

def interpret_query(query: str, columns: list) -> dict:
    try:
        full_prompt = CHART_PROMPT.format(query=query, columns=columns)
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()

        chart_config = json.loads(response_text)
        
        required_keys = {"chart_type", "x", "y"}
        if not all(key in chart_config for key in required_keys):
            raise ValueError("Invalid response from Gemini AI: missing required keys")
        
        if chart_config["x"] not in columns or chart_config["y"] not in columns:
            raise ValueError("Suggested axes not in dataset columns")
        
        logger.info(f"Gemini AI interpreted query '{query}' as: {chart_config}")
        return chart_config
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response: {str(e)}")
        return {"chart_type": "scatter", "x": columns[0], "y": columns[1]}
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise ValueError(f"LLM processing failed: {str(e)}")

def analyze_data(query: str, df: pd.DataFrame) -> str:
    try:
        full_prompt = TREND_PROMPT.format(query=query, columns=df.columns.tolist())
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Trend analysis error: {str(e)}")
        return "Unable to analyze trends due to an error."