import reflex as rx

config = rx.Config(
    app_name="ai_recommendation_engine",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)