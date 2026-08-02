import pandas as pd

required_col = [
"invoice",
"stockcode",
"description",
"quantity",
"invoicedate",
"price",
"customer id"
]

def validate_dataset(file_path):
    df = pd.read_csv(file_path)
    df.columns.str.strip().str.lower()
    missing_columns = []
    for column in required_col:
        if column not in df.columns:
            missing_columns.append(column)
    if missing_columns:
        return False,missing_columns,None
    return True,[],df
