import re
import reflex as rx
from pathlib import Path

from ai_recommendation_engine.backend.hybrid_engine import HybridRecommender
from ai_recommendation_engine.backend.user_store import USER_STORE

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "clean_data.csv"
RECOMMENDER = HybridRecommender(DATA_PATH)


def _split_terms(value: str) -> set[str]:
    if not isinstance(value, str) or value.strip() == "":
        return set()
    return {term.strip() for term in value.split(",") if term.strip()}

CATEGORY_OPTIONS = ["All"] + sorted({
    term
    for value in RECOMMENDER.product_info["Category"].fillna("").astype(str)
    for term in _split_terms(value)
})
BRAND_OPTIONS = ["All"] + sorted({
    term
    for value in RECOMMENDER.product_info["Brand"].fillna("").astype(str)
    for term in _split_terms(value)
})


class UserState(rx.State):

    user_id: str = ""
    password: str = ""
    email: str = ""
    confirm_password: str = ""
    login_status: str = ""
    popup_message: str = ""
    popup_type: str = "success"
    show_popup: bool = False
    theme_mode: str = "light"
    recommendations: list[dict] = []
    filtered_recommendations: list[dict] = []
    search_query: str = ""
    filter_category: str = "All"
    filter_brand: str = "All"
    categories: list[str] = CATEGORY_OPTIONS
    brands: list[str] = BRAND_OPTIONS
    is_existing_user: bool = False
    is_logged_in: bool = False
    loading: bool = False
    last_interactions: list[str] = []

    def set_user_id(self, value):
        self.user_id = value

    def set_password(self, value):
        self.password = value

    def set_email(self, value):
        self.email = value

    def set_confirm_password(self, value):
        self.confirm_password = value

    def set_search_query(self, value):
        self.search_query = value
        self._refresh_filtered_recommendations()

    def set_filter_category(self, value):
        self.filter_category = value
        self._refresh_filtered_recommendations()

    def set_filter_brand(self, value):
        self.filter_brand = value
        self._refresh_filtered_recommendations()

    def _has_valid_user_id(self, user_id: str) -> bool:
        return bool(re.fullmatch(r"\d{1,6}", str(user_id).strip()))

    def _has_valid_password(self, password: str) -> bool:
        return isinstance(password, str) and len(password.strip()) >= 6

    def _format_recommendations(self, df):
        if df is None or df.empty:
            return []

        output = []
        for _, row in df.iterrows():
            output.append({
                "name": str(row.get("Name", "")),
                "category": str(row.get("Category", "")),
                "brand": str(row.get("Brand", "")),
                "image_url": str(row.get("ImageURL", "")),
                "rating": round(float(row.get("Rating", 0)), 1),
                "review_count": int(row.get("Review Count", 0)),
                "score": round(float(row.get("Score", 0)), 2)
            })
        return output

    def _set_recommendations(self, df):
        self.recommendations = self._format_recommendations(df)
        self.filtered_recommendations = list(self.recommendations)
        self.search_query = ""
        self.filter_category = "All"
        self.filter_brand = "All"

    def _refresh_filtered_recommendations(self):
        recommendations = self.recommendations

        if self.search_query.strip():
            search_df = RECOMMENDER.search_products(self.search_query.strip(), top_n=16)
            recommendations = self._format_recommendations(search_df)

        if self.filter_category != "All":
            recommendations = [
                rec for rec in recommendations
                if self.filter_category.lower() in rec["category"].lower()
            ]

        if self.filter_brand != "All":
            recommendations = [
                rec for rec in recommendations
                if self.filter_brand.lower() in rec["brand"].lower()
            ]

        self.filtered_recommendations = recommendations

    def toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"

    def close_popup(self):
        self.show_popup = False

    def _popup(self, message: str, popup_type: str = "success"):
        self.popup_message = message
        self.popup_type = popup_type
        self.show_popup = True

    def handle_login(self):
        if self.user_id == "" or self.password == "":
            self._popup("Please enter both User ID and password.", "error")
            return

        if not self._has_valid_user_id(self.user_id):
            self._popup("User ID must be 1 to 6 digits.", "error")
            return

        if not self._has_valid_password(self.password):
            self._popup("Password must be at least 6 characters.", "error")
            return

        self.loading = True
        self.login_status = ""
        self.is_logged_in = False

        user_id_value = int(self.user_id.strip())

        if not USER_STORE.user_exists(user_id_value):
            self.loading = False
            self._popup("No account found. Please register first.", "error")
            return

        if not USER_STORE.verify_user(user_id_value, self.password):
            self.loading = False
            self._popup("Credentials do not match. Please try again.", "error")
            return

        self.is_existing_user = RECOMMENDER.user_exists(user_id_value)
        self.is_logged_in = True
        self.login_status = f"Welcome back, {self.user_id}!"
        USER_STORE.log_interaction(user_id_value, "login", "successful login")

        if self.is_existing_user:
            recommendations_df = RECOMMENDER.hybrid_recommendations(user_id_value, top_n=10)
        else:
            recommendations_df = RECOMMENDER.new_user_recommendations(top_n=10)

        self._set_recommendations(recommendations_df)
        self.last_interactions = [item["name"] for item in self.recommendations[:5]]
        self.loading = False
        self._popup("Login successful. Enjoy your recommendations!", "success")

        return rx.redirect("/")

    def handle_register(self):
        if self.user_id == "" or self.password == "" or self.confirm_password == "":
            self._popup("Please fill all fields to create your account.", "error")
            return

        if not self._has_valid_user_id(self.user_id):
            self._popup("User ID must be 1 to 6 digits.", "error")
            return

        if not self._has_valid_password(self.password):
            self._popup("Password must be at least 6 characters.", "error")
            return

        if self.password != self.confirm_password:
            self._popup("Passwords do not match.", "error")
            return

        user_id_value = int(self.user_id.strip())
        if USER_STORE.user_exists(user_id_value):
            self._popup("This User ID already exists. Please login.", "error")
            return

        USER_STORE.create_user(user_id_value, self.password, self.email)
        USER_STORE.log_interaction(user_id_value, "register", "account created")

        self.is_existing_user = RECOMMENDER.user_exists(user_id_value)
        self.is_logged_in = True
        self.login_status = f"Account created successfully. Welcome, {self.user_id}!"
        recommendations_df = RECOMMENDER.new_user_recommendations(top_n=10)
        self._set_recommendations(recommendations_df)
        self.last_interactions = [item["name"] for item in self.recommendations[:5]]
        self._popup("Registration successful. You are now logged in.", "success")

        return rx.redirect("/")

    def handle_logout(self):
        self._popup("Logged out successfully.", "success")
        self.user_id = ""
        self.password = ""
        self.email = ""
        self.confirm_password = ""
        self.login_status = ""
        self.recommendations = []
        self.filtered_recommendations = []
        self.search_query = ""
        self.filter_category = "All"
        self.filter_brand = "All"
        self.is_existing_user = False
        self.is_logged_in = False
        self.loading = False
        self.last_interactions = []

        return rx.redirect("/")
