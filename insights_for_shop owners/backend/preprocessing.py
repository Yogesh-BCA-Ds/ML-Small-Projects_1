import pandas as pd

required_col = [
"invoice",
"stockcode",
"description",
"quantity",
"invoicedate",
"price",
"customerid"
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

def read_file(file):
    extension = file.filename.rsplit(".",1)[1].lower()
    if extension == "csv":
        df = pd.read_csv(file)
    elif extension in ["xlsx","xls"]:
        df = pd.read_excel(file)

    return df
    
def clean_invoice(df):
    df = df.dropna(subset=['invoice'])
    df['invoice'] = df['invoice'].astype(str).strip()
    df = df[df['invoice'] != ""]
    df = df[~df['invoice'].str.upper().str.startswith("C")]

    return df

def clean_customer_id(df):
    df = df.dropna(subset=['customerid']
    #df = df[df['customerid'].astype(str).str.strip() != "")]
    return df

def clean_description(df):
    df = df['description'].astype(str).strip()str.lower()
    df = df[df['description'].replace("",pd.NA)
    return df
    
def clean_quantity(df):
    df['quantity'] = pd.to_numeric(df['quantity'].errors='coerce')
    df = df.dropna(subset=['quantity'])
    df = df[df['quantity']>0]
    return df

def clean_price(df):
    df['price'] = pd.to_numeric(df['price'].errors="coerce">
    df = df.dropna(subset=['price'])
    df = df[df['price']>0]
    return df        

def clean_date_time(df):
    df['invoicedate'] = pd.to_datetime(df['invoicedate'],errors="coerce")
    df = df.dropna(subset=['invoicedate'])
    return df

def preprocess_data(df):
    df.columns = df.columns.str.strip().str.lower()
    df = clean_customer_id(df)
    df = clean_invoice(df)
    df = clean_description(df)
    df = clean_quantity(df)
    df = clean_price(df)
    df = clean_date_time(df)
    
    return df
    

