import pandas as pd

def read_file(filename,file_path):
    try:
        if filename.endswith(".csv"):
            df1 = pd.read_csv(file_path)
        else:
            df1 = pd.read_excel(file_path)
        return df1

    except Exception as e:
        print("error:",e)
        return None

    
