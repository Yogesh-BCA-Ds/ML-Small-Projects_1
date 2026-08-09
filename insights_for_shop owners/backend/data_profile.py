import pandas as pd

def profile(df):
    pro_file = {}
    for column in df.columns:
        r = df[column].shape[0]
        if pd.api.types.is_numeric_dtypes(df[column]):
            pro_file[column] = {"column_name":column,
                            "original_dtype":df[column].dtype,
                            "rows":r,
                            "non_null":(df[column].isna()==False).sum()
                            "missing":df["column].isna().sum()
                            "missing_ratio":((df["column].isna().sum())/(df[column].shape[0]))*100
                            "unique":df[column].nunique()
                            "unique_ratio":((df[column].nunique())/(df[column].shape[0]))*100
                            "min":df[column].min()
                            "max":df[column].max()
                            "mean":df[column].mean()
                            "median":df[column].median()
                            "std":df[column].
	
    return pro_file
