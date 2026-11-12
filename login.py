from pathlib import Path
import flet as ft
import api_client

ASSETS = Path(__file__).resolve().parent / "assets"

ACCENT = "#03a800"
FIELD_BG = "#161616"
BORDER = "#2c2c2c"


def build(page: ft.Page, on_success, initial_message=None):
    page.title = "Backbone"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ACCENT)
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0
    page.window.width = 420
    page.window.height = 750
    page.window.min_width = 380
    page.window.min_height = 640
    page.window.icon = str(ASSETS / "icon.ico")

    registering = {"value": False}
    signed_in = {"value": False}

    heading = ft.Text("Welcome back", size=28, weight=ft.FontWeight.W_700)
    subtitle = ft.Text(
        "Sign in to keep your PRs and workouts.",
        size=14,
        color=ft.Colors.GREY_400,
        text_align=ft.TextAlign.CENTER,
    )

    status_icon = ft.Icon(ft.Icons.ERROR_OUTLINE, size=18, color=ft.Colors.RED_300)
    status_text = ft.Text("", size=13, expand=True, color="#ffb4b4")
    status = ft.Container(
        visible=False,
        width=320,
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        bgcolor="#2a1212",
        content=ft.Row(
            [status_icon, status_text],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
    )

    def show_status(message, ok=False):
        status.visible = True
        status.bgcolor = "#102416" if ok else "#2a1212"
        status_icon.icon = ft.Icons.CHECK_CIRCLE_OUTLINE if ok else ft.Icons.ERROR_OUTLINE
        status_icon.color = ACCENT if ok else ft.Colors.RED_300
        status_text.value = message
        status_text.color = "#b7ebc2" if ok else "#ffb4b4"

    def hide_status():
        status.visible = False
        status_text.value = ""

    username = ft.TextField(
        label="Username",
        hint_text="At least 3 characters",
        width=320,
        autofocus=True,
        border_radius=12,
        border_color=BORDER,
        focused_border_color=ACCENT,
        bgcolor=FIELD_BG,
        cursor_color=ACCENT,
        text_size=15,
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        autofill_hints=ft.AutofillHint.USERNAME,
    )
    password = ft.TextField(
        label="Password",
        hint_text="At least 6 characters",
        width=320,
        password=True,
        can_reveal_password=True,
        border_radius=12,
        border_color=BORDER,
        focused_border_color=ACCENT,
        bgcolor=FIELD_BG,
        cursor_color=ACCENT,
        text_size=15,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        autofill_hints=[ft.AutofillHint.PASSWORD],
    )
    confirm = ft.TextField(
        label="Confirm password",
        width=320,
        password=True,
        can_reveal_password=True,
        visible=False,
        border_radius=12,
        border_color=BORDER,
        focused_border_color=ACCENT,
        bgcolor=FIELD_BG,
        cursor_color=ACCENT,
        text_size=15,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        autofill_hints=[ft.AutofillHint.NEW_PASSWORD],
    )

    submit_button = ft.Button(
        "Sign in",
        icon=ft.Icons.ARROW_FORWARD,
        width=320,
        height=48,
        color=ft.Colors.BLACK,
        bgcolor=ACCENT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
    )
    switch_prompt = ft.Text("New here?", size=13, color=ft.Colors.GREY_400)
    switch_button = ft.TextButton("Create an account")
    switch_row = ft.Row(
        [switch_prompt, switch_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=0,
    )

    fields = (username, password, confirm)

    def set_busy(busy):
        submit_button.disabled = busy
        switch_button.disabled = busy
        for field in fields:
            field.disabled = busy
        if busy:
            submit_button.content = "Creating account..." if registering["value"] else "Signing in..."
            submit_button.icon = None
        elif not signed_in["value"]:
            submit_button.content = "Create account" if registering["value"] else "Sign in"
            submit_button.icon = ft.Icons.ARROW_FORWARD

    def apply_mode():
        hide_status()
        confirm.visible = registering["value"]
        confirm.value = ""
        if registering["value"]:
            heading.value = "Create your account"
            subtitle.value = "A username and password are enough to start."
            submit_button.content = "Create account"
            switch_prompt.value = "Already have an account?"
            switch_button.content = "Sign in"
            password.autofill_hints = [ft.AutofillHint.NEW_PASSWORD]
        else:
            heading.value = "Welcome back"
            subtitle.value = "Sign in to keep your PRs and workouts."
            submit_button.content = "Sign in"
            switch_prompt.value = "New here?"
            switch_button.content = "Create an account"
            password.autofill_hints = [ft.AutofillHint.PASSWORD]
        page.update()

    def toggle_mode(e):
        if submit_button.disabled or signed_in["value"]:
            return
        registering["value"] = not registering["value"]
        apply_mode()

    def validation_error():
        name = (username.value or "").strip()
        secret = password.value or ""
        if not name or not secret:
            return "Enter your username and password."
        if len(name) < 3:
            return "Username needs at least 3 characters."
        if len(secret) < 6:
            return "Password needs at least 6 characters."
        if registering["value"] and secret != (confirm.value or ""):
            return "Passwords don't match."
        return None

    def finish(message, ok=False):
        show_status(message, ok=ok)
        if ok:
            signed_in["value"] = True
            submit_button.content = "Signed in"
            submit_button.icon = ft.Icons.CHECK
            submit_button.disabled = True
            switch_row.visible = False
            for field in fields:
                field.disabled = True
        else:
            set_busy(False)
        page.update()

    def authenticate():
        name = username.value.strip()
        secret = password.value
        try:
            if registering["value"]:
                api_client.register(name, secret)
            if not api_client.login(name, secret):
                finish("That username and password don't match.")
                return
            on_success()
        except ValueError as error:
            finish(str(error))
        except api_client.ApiError as error:
            finish(str(error))

    def submit(e):
        if signed_in["value"] or submit_button.disabled:
            return
        message = validation_error()
        if message:
            show_status(message)
            page.update()
            return
        set_busy(True)
        hide_status()
        page.update()
        page.run_thread(authenticate)

    def on_edit(e):
        if status.visible and not signed_in["value"]:
            hide_status()
            page.update()

    if initial_message:
        show_status(initial_message)

    username.on_change = on_edit
    password.on_change = on_edit
    confirm.on_change = on_edit
    username.on_submit = submit
    password.on_submit = submit
    confirm.on_submit = submit
    submit_button.on_click = submit
    switch_button.on_click = toggle_mode

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.symmetric(horizontal=28, vertical=24),
                content=ft.Column(
                    [
                        ft.Container(
                            width=88,
                            height=88,
                            alignment=ft.Alignment.CENTER,
                            border=ft.Border.all(2, ACCENT),
                            border_radius=28,
                            content=ft.Image(src="icon.png", width=64, height=64),
                        ),
                        ft.Text(
                            "BACKBONE",
                            size=13,
                            weight=ft.FontWeight.W_700,
                            color=ACCENT,
                            style=ft.TextStyle(letter_spacing=3),
                        ),
                        heading,
                        subtitle,
                        ft.Container(height=8),
                        username,
                        password,
                        confirm,
                        status,
                        submit_button,
                        switch_row,
                    ],
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
        )
    )


def _run(page: ft.Page):
    import main as app

    app.main(page)


if __name__ == "__main__":
    ft.run(_run)
