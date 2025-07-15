# backend/utils.py
import pandas as pd

def validate_dataset(df: pd.DataFrame) -> bool:
    if df.empty:
        raise ValueError("Dataset is empty")
    if len(df.columns) < 2:
        raise ValueError("Dataset must have at least 2 columns")
    return True

def sanitize_column_name(name: str) -> str:
    return name.strip().replace(" ", "_")