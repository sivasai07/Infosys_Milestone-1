import reflex as rx
from ai_recommendation_engine.pages.index import index
from ai_recommendation_engine.pages.login import login
from ai_recommendation_engine.pages.register import register


app = rx.App()

app.add_page(index, route="/")
app.add_page(login, route="/login")
app.add_page(register, route="/register")