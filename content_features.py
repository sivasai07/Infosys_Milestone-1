import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def prepare_unique_products(df):
    """
    Keep only unique products for content-based filtering
    """
    product_df = df[[
        "ProdID",
        "Category",
        "Brand",
        "Description",
        "Tags"
    ]].drop_duplicates(subset="ProdID")

    product_df.reset_index(drop=True, inplace=True)

    return product_df


def combine_text_features(product_df):
    """
    Combine product text features into single column
    """
    product_df["Combined_Features"] = (
        product_df["Category"].astype(str) + " " +
        product_df["Brand"].astype(str) + " " +
        product_df["Description"].astype(str) + " " +
        product_df["Tags"].astype(str)
    )

    return product_df


def create_tfidf_matrix(product_df):
    """
    Create TF-IDF matrix for products
    """
    tfidf = TfidfVectorizer(
        stop_words="english",
        max_features=5000
    )

    tfidf_matrix = tfidf.fit_transform(product_df["Combined_Features"])

    return tfidf_matrix, tfidf


if __name__ == "__main__":
    from preprocess_data import load_data, clean_data

    data_path = "data/clean_data.csv"

    df = load_data(data_path)
    df_clean = clean_data(df)

    product_df = prepare_unique_products(df_clean)
    product_df = combine_text_features(product_df)

    tfidf_matrix, tfidf_model = create_tfidf_matrix(product_df)

    print("Number of Unique Products:", product_df.shape[0])
    print("TF-IDF Matrix Shape:", tfidf_matrix.shape)
    print("Number of Features:", len(tfidf_model.get_feature_names_out()))
