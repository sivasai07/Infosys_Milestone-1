from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ai_recommendation_engine.backend.cleaning_data import clean_data, load_data
from ai_recommendation_engine.backend.rating_based import RatingBasedRecommender


class HybridRecommender:

    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)

        df = load_data(self.data_path)
        df = clean_data(df)

        df["UserID"] = df["UserID"].astype(int)
        df["ProdID"] = df["ProdID"].astype(int)

        self.rating_recommender = RatingBasedRecommender(self.data_path)

        product_metadata = df.groupby("ProdID").agg({
            "Description": "first",
            "Tags": "first"
        }).fillna("")

        self.products = self.rating_recommender.products.merge(
            product_metadata,
            left_on="ProdID",
            right_index=True,
            how="left"
        )

        self.products["Description"] = self.products["Description"].fillna("")
        self.products["Tags"] = self.products["Tags"].fillna("")

        self.products["combined_features"] = (
            self.products["Tags"].astype(str) + " " +
            self.products["Tags"].astype(str) + " " +
            self.products["Tags"].astype(str) + " " +
            self.products["Category"].astype(str) + " " +
            self.products["Category"].astype(str) + " " +
            self.products["Brand"].astype(str) + " " +
            self.products["Description"].astype(str)
        )

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.products["combined_features"]
        )

        self.product_index = {
            int(prod_id): idx
            for prod_id, idx in zip(self.products["ProdID"], self.products.index)
        }

        self.product_info = self.products.set_index("ProdID")[[
            "Name",
            "Category",
            "Brand",
            "Rating",
            "Review Count",
            "Score"
        ]]

        self.user_item_matrix = df.pivot_table(
            index="UserID",
            columns="ProdID",
            values="Rating",
            aggfunc="mean",
            fill_value=0
        )

        self.user_ids = set(self.user_item_matrix.index.astype(int))

        self.item_similarity = cosine_similarity(self.user_item_matrix.T)
        self.item_similarity_df = pd.DataFrame(
            self.item_similarity,
            index=self.user_item_matrix.columns,
            columns=self.user_item_matrix.columns
        )

    def user_exists(self, user_id: int | None) -> bool:
        return user_id in self.user_ids if user_id is not None else False

    def _normalize(self, scores: pd.Series) -> pd.Series:
        if scores.empty:
            return scores
        minimum = scores.min()
        maximum = scores.max()
        if maximum == minimum:
            return pd.Series(1.0, index=scores.index)
        return (scores - minimum) / (maximum - minimum)

    def get_collaborative_scores(self, user_id: int) -> pd.Series:
        if user_id not in self.user_item_matrix.index:
            return pd.Series(dtype=float)

        user_ratings = self.user_item_matrix.loc[user_id]
        raw_scores = self.item_similarity_df.dot(user_ratings)
        denom = self.item_similarity_df.abs().sum(axis=1).replace(0, 1)
        candidate_scores = raw_scores.div(denom)

        unseen_items = user_ratings[user_ratings == 0].index
        return candidate_scores.loc[unseen_items].sort_values(ascending=False)

    def get_content_scores(self, user_id: int) -> pd.Series:
        if user_id not in self.user_item_matrix.index:
            return pd.Series(dtype=float)

        user_ratings = self.user_item_matrix.loc[user_id]
        rated_items = user_ratings[user_ratings > 0]
        rated_items = rated_items[rated_items.index.isin(self.product_index)]

        if rated_items.empty:
            return pd.Series(dtype=float)

        item_indices = [self.product_index[int(prod_id)] for prod_id in rated_items.index]
        item_vector = self.tfidf_matrix[item_indices]
        weights = rated_items.values

        user_profile = np.average(item_vector.toarray(), axis=0, weights=weights)
        similarity_scores = cosine_similarity(
            self.tfidf_matrix,
            user_profile.reshape(1, -1)
        ).flatten()

        content_series = pd.Series(similarity_scores, index=self.products["ProdID"])
        return content_series[~content_series.index.isin(rated_items.index)].sort_values(ascending=False)

    def hybrid_recommendations(self, user_id: int, top_n: int = 10) -> pd.DataFrame:
        if not self.user_exists(user_id):
            return self.new_user_recommendations(top_n)

        collab_scores = self.get_collaborative_scores(user_id)
        content_scores = self.get_content_scores(user_id)

        if collab_scores.empty and content_scores.empty:
            return self.new_user_recommendations(top_n)

        collab_norm = self._normalize(collab_scores)
        content_norm = self._normalize(content_scores)

        candidate_ids = collab_norm.index.union(content_norm.index)
        hybrid_scores = pd.Series(0.0, index=candidate_ids)
        hybrid_scores = hybrid_scores.add(collab_norm.reindex(candidate_ids, fill_value=0) * 0.6, fill_value=0)
        hybrid_scores = hybrid_scores.add(content_norm.reindex(candidate_ids, fill_value=0) * 0.4, fill_value=0)

        top_items = hybrid_scores.sort_values(ascending=False).head(top_n)
        recommendations = self.product_info.loc[top_items.index].copy()
        recommendations["Score"] = top_items.values
        recommendations = recommendations.sort_values(by="Score", ascending=False).reset_index()
        return recommendations[["ProdID", "Name", "Category", "Brand", "Rating", "Review Count", "Score"]]

    def new_user_recommendations(self, top_n: int = 10) -> pd.DataFrame:
        return self.rating_recommender.top_rated(top_n)

    def search_products(self, query: str, top_n: int = 10) -> pd.DataFrame:
        query = str(query).strip()
        if not query:
            return self.new_user_recommendations(top_n)

        matches = self.products[
            self.products["Name"].str.contains(query, case=False, na=False) |
            self.products["Brand"].str.contains(query, case=False, na=False) |
            self.products["Category"].str.contains(query, case=False, na=False)
        ]

        if matches.empty:
            return self.new_user_recommendations(top_n)

        return matches.head(top_n)[["ProdID", "Name", "Category", "Brand", "Rating", "Review Count", "Score"]]

    def similar_products(self, prod_id: int, top_n: int = 6) -> pd.DataFrame:
        if prod_id not in self.product_index:
            return self.new_user_recommendations(top_n)

        prod_idx = self.product_index[prod_id]
        scores = cosine_similarity(
            self.tfidf_matrix[prod_idx],
            self.tfidf_matrix
        ).flatten()
        similarity_series = pd.Series(scores, index=self.products["ProdID"])
        similarity_series = similarity_series.drop(prod_id)
        top_items = similarity_series.sort_values(ascending=False).head(top_n)
        recommendations = self.product_info.loc[top_items.index].copy()
        recommendations["Score"] = top_items.values
        recommendations = recommendations.sort_values(by="Score", ascending=False).reset_index()
        return recommendations[["ProdID", "Name", "Category", "Brand", "Rating", "Review Count", "Score"]]
