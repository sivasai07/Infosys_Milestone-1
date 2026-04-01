import reflex as rx
from ai_recommendation_engine.components.navbar import navbar
from ai_recommendation_engine.state.user_state import UserState


def _popup_banner():
    return rx.cond(
        UserState.show_popup,
        rx.box(
            rx.hstack(
                rx.text(UserState.popup_message, color="white", font_weight="semibold"),
                rx.button(
                    "✕",
                    on_click=UserState.close_popup,
                    bg="transparent",
                    color="white",
                    border="none",
                    _hover={"bg": "rgba(255,255,255,0.12)"}
                ),
                justify="between",
                width="100%"
            ),
            bg=rx.cond(UserState.popup_type == "success", "#2563EB", "#DC2626"),
            padding="18px 22px",
            border_radius="16px",
            box_shadow="0px 15px 40px rgba(15, 23, 42, 0.18)",
            width="100%",
            max_width="840px",
            position="sticky",
            top="96px",
            z_index="1000"
        )
    )


def _recommendation_card(item, text_color, section_text):
    return rx.box(
        rx.box(
            style={
                "backgroundImage": f"url({item.get('image_url', '')})",
                "backgroundSize": "cover",
                "backgroundPosition": "center",
                "height": "220px"
            },
            width="100%"
        ),
        rx.vstack(
            rx.heading(item["name"], size="5", color=text_color),
            rx.text(item["brand"], color=section_text, font_size="sm"),
            rx.text(item["category"], color=section_text, font_size="xs"),
            rx.hstack(
                rx.badge(str(item["rating"]), color_scheme="green", variant="solid"),
                rx.text(f"{item['review_count']} reviews", color=section_text, font_size="sm"),
                spacing="3"
            ),
            spacing="3",
            padding="22px"
        ),
        bg="white",
        border_radius="20px",
        box_shadow="0px 10px 35px rgba(15, 23, 42, 0.08)",
        overflow="hidden",
        width="100%"
    )


def index():
    page_bg = rx.cond(UserState.theme_mode == "dark", "#0F172A", "#F8FAFC")
    text_color = rx.cond(UserState.theme_mode == "dark", "white", "#334155")
    panel_bg = rx.cond(UserState.theme_mode == "dark", "rgba(255,255,255,0.08)", "white")
    section_text = rx.cond(UserState.theme_mode == "dark", "#E2E8F0", "gray")

    return rx.box(
        navbar(),
        _popup_banner(),
        rx.center(
            rx.vstack(
                rx.vstack(
                    rx.heading("AI Recommendation Engine", size="8", color=text_color),
                    rx.text(
                        "Smart product recommendations powered by hybrid AI and user behavior.",
                        color=section_text,
                        font_size="lg"
                    ),
                    rx.cond(
                        UserState.is_logged_in,
                        rx.button(
                            "View Recommendations",
                            on_click=rx.redirect("/"),
                            bg="#2563EB",
                            color="white",
                            border_radius="14px",
                            padding="18px 26px"
                        ),
                        rx.hstack(
                            rx.button(
                                "Login",
                                on_click=rx.redirect("/login"),
                                bg="#2563EB",
                                color="white",
                                border_radius="14px",
                                padding="18px 26px"
                            ),
                            rx.button(
                                "Register",
                                on_click=rx.redirect("/register"),
                                bg="transparent",
                                color="#2563EB",
                                border="1px solid #2563EB",
                                border_radius="14px",
                                padding="18px 26px"
                            ),
                            spacing="4"
                        )
                    ),
                    spacing="5",
                    width="100%",
                    align="center"
                ),
                rx.cond(
                    UserState.is_logged_in,
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.heading(f"Hello, {UserState.user_id}", size="6", color=text_color),
                                rx.badge("Hybrid AI", color_scheme="blue", variant="soft"),
                                spacing="4"
                            ),
                            rx.text("Search products or filter by category and brand.", color=section_text)
                        ),
                        padding="24px",
                        bg=panel_bg,
                        border_radius="20px",
                        width="100%",
                        box_shadow="0px 10px 35px rgba(15, 23, 42, 0.08)"
                    ),
                    rx.box(
                        rx.heading("Welcome to AI Shop", size="6", color=text_color),
                        rx.text("Login or register to see personalized product recommendations.", color=section_text),
                        rx.button(
                            "Get Started",
                            on_click=rx.redirect("/login"),
                            bg="#2563EB",
                            color="white",
                            border_radius="12px",
                            padding="18px 30px"
                        ),
                        spacing="4",
                        padding="24px",
                        bg=panel_bg,
                        border_radius="20px",
                        width="100%",
                        box_shadow="0px 10px 35px rgba(15, 23, 42, 0.08)"
                    )
                ),
                rx.cond(
                    UserState.is_logged_in,
                    rx.vstack(
                        rx.hstack(
                            rx.input(
                                placeholder="Search categories, brands or products",
                                on_change=UserState.set_search_query,
                                value=UserState.search_query,
                                width="100%",
                                bg="white",
                                border_radius="16px",
                                box_shadow="0px 8px 20px rgba(15, 23, 42, 0.06)",
                                padding="18px"
                            ),
                            spacing="4"
                        ),
                        rx.hstack(
                            rx.select(
                                UserState.categories,
                                value=UserState.filter_category,
                                on_change=UserState.set_filter_category,
                                width="180px",
                                border_radius="16px",
                                padding="18px"
                            ),
                            rx.select(
                                UserState.brands,
                                value=UserState.filter_brand,
                                on_change=UserState.set_filter_brand,
                                width="180px",
                                border_radius="16px",
                                padding="18px"
                            ),
                            spacing="4",
                            width="100%"
                        )
                    ),
                    None
                ),
                rx.cond(
                    UserState.is_logged_in,
                    rx.cond(
                        UserState.filtered_recommendations == [],
                        rx.text("No recommendations match the selected filters. Try a different search.", color=section_text),
                        rx.grid(
                            rx.foreach(
                                UserState.filtered_recommendations,
                                lambda item: _recommendation_card(item, text_color, section_text)
                            ),
                            columns="repeat( auto-fit, minmax(260px, 1fr) )",
                            gap="22px"
                        )
                    ),
                    rx.vstack(
                        rx.heading("Explore top products", size="6", color=text_color),
                        rx.text("Please login to view your personalized recommendations.", color=section_text)
                    )
                ),
                spacing="8"
            ),
            min_height="85vh",
            bg=page_bg,
            padding="40px 24px"
        )
    )