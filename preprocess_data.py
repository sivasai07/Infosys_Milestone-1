import pandas as pd
import numpy as np


def load_data(file_path):
    return pd.read_csv(file_path)


def clean_data(df):
    # Drop unwanted column if exists
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

    # Rename problematic column
    if "User's ID" in df.columns:
        df.rename(columns={"User's ID": "UserID"}, inplace=True)

    # Replace invalid placeholders with NaN
    df.replace(["", " ", "NULL", "null"], np.nan, inplace=True)

    # Convert ID columns to numeric safely
    if "UserID" in df.columns:
        df["UserID"] = pd.to_numeric(df["UserID"], errors="coerce")

    if "ProdID" in df.columns:
        df["ProdID"] = pd.to_numeric(df["ProdID"], errors="coerce")

    if "Rating" in df.columns:
        df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")

    # Remove invalid IDs (NaN, zero, negative)
    if "UserID" in df.columns:
        df = df[df["UserID"].notna()]
        df = df[df["UserID"] > 0]

    if "ProdID" in df.columns:
        df = df[df["ProdID"].notna()]
        df = df[df["ProdID"] > 0]

    # Remove invalid ratings (if 0 means no rating)
    if "Rating" in df.columns:
        df = df[df["Rating"].notna()]
        df = df[df["Rating"] > 0]

    # Clean text columns
    text_columns = df.select_dtypes(include=["object"]).columns
    for col in text_columns:
        df[col] = df[col].fillna("")
        df[col] = df[col].str.replace("|", "", regex=False)

    # Reset index
    df.reset_index(drop=True, inplace=True)

    return df


def create_user_item_matrix(df):
    user_col = "UserID"
    item_col = "ProdID"

    if user_col in df.columns and item_col in df.columns:
        user_item_matrix = df.pivot_table(
            index=user_col,
            columns=item_col,
            values="Rating",     # Now rating-based
            aggfunc="mean",
            fill_value=0
        )
        return user_item_matrix
    else:
        print("Required columns not found.")
        return None


if __name__ == "__main__":
    data_path = "data/clean_data.csv"

    df = load_data(data_path)
    print("Original Shape:", df.shape)

    df_clean = clean_data(df)
    print("Cleaned Shape:", df_clean.shape)

    print("Min UserID:", df_clean["UserID"].min())
    print("Min ProdID:", df_clean["ProdID"].min())
    print("Min Rating:", df_clean["Rating"].min())

    user_item = create_user_item_matrix(df_clean)

    if user_item is not None:
        print("User-Item Matrix Created")
        print("Matrix Shape:", user_item.shape)
        print(user_item.head())
