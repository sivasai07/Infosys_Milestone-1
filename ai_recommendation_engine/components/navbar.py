import reflex as rx
from ai_recommendation_engine.state.user_state import UserState


def navbar():
    return rx.flex(
        rx.link(
            rx.heading("AI Shop", size="6", color="white"),
            href="/",
            style={"textDecoration": "none"}
        ),

        rx.spacer(),

        rx.hstack(
            rx.link("Home", href="/", color="white"),
            rx.cond(
                UserState.is_logged_in,
                rx.link("Recommendations", href="/", color="white"),
                rx.link("Login", href="/login", color="white")
            ),
            rx.cond(
                UserState.is_logged_in,
                rx.button(
                    "Logout",
                    on_click=UserState.handle_logout,
                    bg="transparent",
                    color="white",
                    border="1px solid rgba(255,255,255,0.35)",
                    border_radius="12px",
                    padding="8px 16px"
                ),
                rx.link("Register", href="/register", color="white")
            ),
            rx.button(
                rx.cond(UserState.theme_mode == "light", "☀️", "🌙"),
                on_click=UserState.toggle_theme,
                bg="transparent",
                color="white",
                border="1px solid rgba(255,255,255,0.35)",
                border_radius="12px",
                padding="8px 14px"
            ),
            spacing="6"
        ),

        rx.cond(
            UserState.is_logged_in,
            rx.text(f"Welcome, {UserState.user_id}", color="white", font_size="sm")
        ),

        padding="18px 32px",
        bg="linear-gradient(90deg, #1E3A8A, #2563EB)",
        width="100%",
        align="center",
        position="sticky",
        top="0",
        z_index="999"
    )