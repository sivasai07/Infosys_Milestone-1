import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from cleaning_data import load_data, clean_data


class CollaborativeRecommender:

    def __init__(self, data_path):

        df = load_data(data_path)
        df = clean_data(df)

        # Ensure IDs are integers
        df["UserID"] = df["UserID"].astype(int)
        df["ProdID"] = df["ProdID"].astype(int)

        # Create user-item rating matrix
        self.user_item_matrix = df.pivot_table(
            index="UserID",
            columns="ProdID",
            values="Rating",
            fill_value=0
        )

        # Item-item similarity matrix
        self.item_similarity = cosine_similarity(self.user_item_matrix.T)

        self.item_similarity_df = pd.DataFrame(
            self.item_similarity,
            index=self.user_item_matrix.columns,
            columns=self.user_item_matrix.columns
        )

        # Product information table
        self.product_info = df[[
            "ProdID",
            "Name",
            "Brand",
            "Category",
            "Review Count"
        ]].drop_duplicates(subset="ProdID")

        self.product_info["ProdID"] = self.product_info["ProdID"].astype(int)

        self.product_info.set_index("ProdID", inplace=True)

    def recommend(self, product_name, top_n=10):

        matches = self.product_info[
            self.product_info["Name"].str.contains(product_name, case=False, na=False)
        ]

        if matches.empty:
            print("Product not found")
            return pd.DataFrame()

        matches = matches.head(3)

        print("\nPossible Matches:")

        for pid, row in matches.iterrows():
            print(f"{int(pid)} - {row['Name']}")

        product_id = int(input("\nSelect product ID: "))

        if product_id not in self.item_similarity_df.index:
            print("Product not in interaction matrix")
            return pd.DataFrame()

        similarity_scores = self.item_similarity_df[product_id]

        similarity_scores = similarity_scores.sort_values(ascending=False)

        similarity_scores = similarity_scores.iloc[1:top_n+1]

        recommended_ids = similarity_scores.index

        recommendations = self.product_info.loc[recommended_ids][[
            "Name",
            "Category",
            "Review Count",
            "Brand"
        ]]

        return recommendations


if __name__ == "__main__":

    data_path = "data/clean_data.csv"

    recommender = CollaborativeRecommender(data_path)

    product = input("Enter product name: ")

    recommendations = recommender.recommend(product)

    print("\nRecommended Products:")
    print(recommendations)