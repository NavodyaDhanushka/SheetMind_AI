import pandas as pd

def read_excel(file_path):
    df = pd.read_excel(file_path)
    return df.to_dict(orient="records")

def row_to_context(row):
    return "\n".join([f"{key}: {value}" for key, value in row.items()])
