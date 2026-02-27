import pandas as pd
from cleaning_data import load_data, clean_data


class RatingBasedRecommender:

    def __init__(self, data_path):

        df = load_data(data_path)
        df = clean_data(df)

        # Ensure correct data types
        df["ProdID"] = df["ProdID"].astype(int)
        df["Review Count"] = df["Review Count"].astype(int)

        # Product level aggregation
        self.products = df.groupby("ProdID").agg({
            "Name": "first",
            "Category": "first",
            "Brand": "first",
            "Rating": "mean",
            "Review Count": "mean"
        }).reset_index()

        # Global average rating
        self.C = self.products["Rating"].mean()

        # Minimum reviews threshold (75th percentile)
        self.m = self.products["Review Count"].quantile(0.75)

        # Compute weighted score
        self.products["Score"] = self.products.apply(self.weighted_rating, axis=1)

    def weighted_rating(self, row):

        v = row["Review Count"]
        R = row["Rating"]

        return (v/(v+self.m) * R) + (self.m/(v+self.m) * self.C)

    def top_rated(self, n=10):

        recommendations = self.products.sort_values(
            by="Score",
            ascending=False
        ).head(n)

        return recommendations[[
            "Name",
            "Category",
            "Rating",
            "Review Count",
            "Brand"
        ]]

    def popular_products(self, n=10):

        # Popularity fallback (based on review count)
        recommendations = self.products.sort_values(
            by="Review Count",
            ascending=False
        ).head(n)

        return recommendations[[
            "Name",
            "Category",
            "Rating",
            "Review Count",
            "Brand"
        ]]


if __name__ == "__main__":

    data_path = "data/clean_data.csv"

    recommender = RatingBasedRecommender(data_path)

    print("\nTop Rated Products:")
    print(recommender.top_rated(10))

    print("\nMost Popular Products:")
    print(recommender.popular_products(10))