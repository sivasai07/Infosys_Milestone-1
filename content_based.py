import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from cleaning_data import load_data, clean_data


class ContentBasedRecommender:

    def __init__(self, data_path):
        # Load and clean dataset
        df = load_data(data_path)
        df = clean_data(df)

        # Keep unique products
        self.products = df[[
            "ProdID",
            "Name",
            "Category",
            "Brand",
            "Description",
            "Tags",
            "Review Count"
        ]].drop_duplicates(subset="ProdID")

        self.products.reset_index(drop=True, inplace=True)

        # Feature weighting
        self.products["combined_features"] = (
            self.products["Tags"].astype(str) + " " +
            self.products["Tags"].astype(str) + " " +
            self.products["Tags"].astype(str) + " " +
            self.products["Category"].astype(str) + " " +
            self.products["Category"].astype(str) + " " +
            self.products["Brand"].astype(str) + " " +
            self.products["Description"].astype(str)
        )

        # Improved TF-IDF
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2
        )

        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.products["combined_features"]
        )

        # Similarity matrix
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)

    def recommend(self, product_name, top_n=10):

        matches = self.products[
            self.products["Name"].str.contains(product_name, case=False, na=False)
        ]

        if matches.empty:
            print("Product not found")
            return pd.DataFrame()

        # Show top 3 matched products
        matches = matches.head(3)

        print("\nPossible Matches:")
        for i, row in matches.iterrows():
            print(f"{i} - {row['Name']}")

        # Ask user to select correct product
        idx = int(input("\nSelect product index: "))

        print("\nSelected Product:")
        print(self.products.loc[idx, "Name"])

        similarity_scores = list(enumerate(self.similarity_matrix[idx]))

        similarity_scores = sorted(
            similarity_scores,
            key=lambda x: x[1],
            reverse=True
        )

        similarity_scores = similarity_scores[1:top_n+1]

        product_indices = [i[0] for i in similarity_scores]

        return self.products.iloc[product_indices][[
            "Name",
            "Category",
            "Review Count",
            "Brand"
        ]]


if __name__ == "__main__":

    data_path = "data/clean_data.csv"

    recommender = ContentBasedRecommender(data_path)

    product = input("Enter product name: ")

    recommendations = recommender.recommend(product)

    print("\nRecommended Products:")
    print(recommendations)