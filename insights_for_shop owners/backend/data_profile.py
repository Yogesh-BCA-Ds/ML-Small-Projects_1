import pandas as pd

def profile(df):
    pro_file = {}
    for column in df.columns:
        r = df[column].shape[0]
        if pd.api.types.is_numeric_dtype(df[column]):
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            IQR = q3 - q1
            lower = q1 - 1.5 * IQR
            upper = q3 + 1.5 * IQR
            outliers = ((df[column] < lower) | (df[column] > upper)).sum()
            pro_file[column] = {
                "column_name": column,
                "original_dtype": df[column].dtype,
                "rows": r,
                "non_null": df[column].notna().sum(),
                "missing": df[column].isna().sum(),
                "missing_ratio": df[column].isna().sum() / df[column].shape[0] * 100,
                "unique": df[column].nunique(),
                "unique_ratio": df[column].nunique() / df[column].shape[0] * 100,
                "integer_like_ratio": (df[column].dropna() % 1 == 0).mean() * 100,
                "min": df[column].min(),
                "max": df[column].max(),
                "mean": df[column].mean(),
                "median": df[column].median(),
                "std": df[column].std(),
                "negative": (df[column] < 0).sum(),
                "zero": (df[column] == 0).sum(),
                "skewness": df[column].skew(),
                "outliers": outliers,
            }
        elif pd.api.types.is_object_dtype(df[column]):
            counts = df[column].value_counts()
            lengths = df[column].dropna().astype(str).str.len()
            numeric_test = pd.to_numeric(df[column], errors="coerce")
            date_test = pd.to_datetime(df[column], errors="coerce")
            values = df[column].dropna().astype(str)
            digit_only = values.str.fullmatch(r"\d+").mean() * 100
            alpha_only = values.str.fullmatch(r"[A-Za-z]+").mean() * 100
            alpha_numeric = values.str.fullmatch(r"[A-Za-z0-9]+").mean() * 100

            pro_file[column] = {
                "column_name": column,
                "original_dtype": df[column].dtype,
                "cardinality": df[column].nunique(),
                'rows':r,
                "top_values": counts.head(5).to_dict(),
                "rare_category_count": (counts / counts.sum() < 0.01).sum(),
                "min_length": lengths.min(),
                "max_length": lengths.max(),
                "avg_length": lengths.mean(),
                "numeric_like": numeric_test.notna().sum(),
                "numeric_like_ratio": numeric_test.notna().sum() / df[column].notna().sum() * 100,
                "date_like": date_test.notna().sum(),
                "date_like_ratio": date_test.notna().sum() / df[column].notna().sum() * 100,
                "digit_only_ratio": digit_only,
                "alpha_only_ratio": alpha_only,
                "alpha_numeric_ratio": alpha_numeric,
            }

    return pro_file
