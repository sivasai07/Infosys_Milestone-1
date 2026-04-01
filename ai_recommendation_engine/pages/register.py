import reflex as rx
from ai_recommendation_engine.state.user_state import UserState
from ai_recommendation_engine.components.navbar import navbar


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
            max_width="520px",
            position="sticky",
            top="96px",
            z_index="1000"
        )
    )


def register():
    page_bg = rx.cond(UserState.theme_mode == "dark", "#0F172A", "#EFF6FF")
    text_color = rx.cond(UserState.theme_mode == "dark", "white", "#1E293B")
    panel_bg = rx.cond(UserState.theme_mode == "dark", "#1E293B", "white")
    sub_text = rx.cond(UserState.theme_mode == "dark", "#CBD5E1", "#64748B")

    return rx.box(
        navbar(),
        _popup_banner(),
        rx.center(
            rx.box(
                rx.vstack(
                    rx.heading("Create an Account", size="6", color=text_color),
                    rx.text("Register to save your preferences and get instant recommendations.", color=sub_text),

                    rx.vstack(
                        rx.text("User ID", color=sub_text, font_size="sm"),
                        rx.input(
                            placeholder="Enter User ID (numbers only)",
                            value=UserState.user_id,
                            on_change=UserState.set_user_id,
                            width="100%",
                            bg=rx.cond(UserState.theme_mode == "dark", "#0F172A", "white"),
                            color=rx.cond(UserState.theme_mode == "dark", "#E2E8F0", "#0F172A"),
                            border="1px solid #CBD5E1",
                            border_radius="16px",
                            padding="18px"
                        ),
                        spacing="2"
                    ),

                    rx.vstack(
                        rx.text("Email", color=sub_text, font_size="sm"),
                        rx.input(
                            placeholder="Enter Email (optional)",
                            value=UserState.email,
                            on_change=UserState.set_email,
                            width="100%",
                            bg=rx.cond(UserState.theme_mode == "dark", "#0F172A", "white"),
                            color=rx.cond(UserState.theme_mode == "dark", "#E2E8F0", "#0F172A"),
                            border="1px solid #CBD5E1",
                            border_radius="16px",
                            padding="18px"
                        ),
                        spacing="2"
                    ),

                    rx.vstack(
                        rx.text("Password", color=sub_text, font_size="sm"),
                        rx.input(
                            type="password",
                            placeholder="Create Password",
                            value=UserState.password,
                            on_change=UserState.set_password,
                            width="100%",
                            bg=rx.cond(UserState.theme_mode == "dark", "#0F172A", "white"),
                            color=rx.cond(UserState.theme_mode == "dark", "#E2E8F0", "#0F172A"),
                            border="1px solid #CBD5E1",
                            border_radius="16px",
                            padding="18px"
                        ),
                        spacing="2"
                    ),

                    rx.vstack(
                        rx.text("Confirm Password", color=sub_text, font_size="sm"),
                        rx.input(
                            type="password",
                            placeholder="Confirm Password",
                            value=UserState.confirm_password,
                            on_change=UserState.set_confirm_password,
                            width="100%",
                            bg=rx.cond(UserState.theme_mode == "dark", "#0F172A", "white"),
                            color=rx.cond(UserState.theme_mode == "dark", "#E2E8F0", "#0F172A"),
                            border="1px solid #CBD5E1",
                            border_radius="16px",
                            padding="18px"
                        ),
                        spacing="2"
                    ),

                    rx.button(
                        "Register",
                        on_click=UserState.handle_register,
                        width="100%",
                        bg="#2563EB",
                        color="white",
                        border_radius="14px",
                        padding="18px"
                    ),

                    rx.hstack(
                        rx.text("Already registered?", color=sub_text),
                        rx.link("Login here", href="/login", color="#2563EB"),
                        spacing="2"
                    ),
                    spacing="4"
                ),
                padding="40px",
                bg=panel_bg,
                border_radius="24px",
                box_shadow="0px 10px 35px rgba(0,0,0,0.15)",
                width="420px"
            ),
            height="92vh",
            bg=page_bg,
            width="100%"
        )
    )