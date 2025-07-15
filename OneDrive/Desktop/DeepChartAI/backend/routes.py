# backend/routes.py
import pandas as pd
from io import StringIO
import json
from typing import Dict, Optional
from chart_generator import create_chart
from llm_integration import interpret_query, analyze_data
from utils import validate_dataset
import logging

logger = logging.getLogger(__name__)

def generate_chart(query: str, data_content: bytes, chart_type: Optional[str] = None) -> Dict:
    try:
        if data_content.decode('utf-8').startswith('{'):
            df = pd.DataFrame(json.loads(data_content))
        else:
            df = pd.read_csv(StringIO(data_content.decode('utf-8')))
        validate_dataset(df)

        if chart_type:
            chart_config = {"chart_type": chart_type, "x": df.columns[0], "y": df.columns[1]}
        else:
            chart_config = interpret_query(query, df.columns.tolist())
        
        chart_type = chart_config["chart_type"]
        x_axis = chart_config["x"]
        y_axis = chart_config["y"]

        if x_axis not in df.columns or y_axis not in df.columns:
            raise ValueError(f"Columns '{x_axis}' or '{y_axis}' not found in dataset")

        chart_data = df[[x_axis, y_axis]].to_dict(orient="list")
        code = create_chart(chart_type, x_axis, y_axis)

        logger.info(f"Generated {chart_type} chart for query: {query}")
        return {
            "chart_type": chart_type,
            "x_axis": x_axis,
            "y_axis": y_axis,
            "data": chart_data,
            "code": code,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Chart generation failed: {str(e)}")
        raise

def analyze_trends(query: str, file_content: bytes) -> Dict:
    try:
        df = pd.read_csv(StringIO(file_content.decode('utf-8')))
        validate_dataset(df)
        insights = analyze_data(query, df)
        return {"insights": insights, "status": "success"}
    except Exception as e:
        logger.error(f"Trend analysis failed: {str(e)}")
        raise