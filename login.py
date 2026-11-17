from pathlib import Path
import flet as ft
import api_client
import i18n as tr

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

    heading = ft.Text(tr.t("welcome_back"), size=28, weight=ft.FontWeight.W_700)
    subtitle = ft.Text(
        tr.t("sign_in_to_keep_your_prs_and_workouts"),
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
        label=tr.t("username"),
        hint_text=tr.t("at_least_3_characters"),
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
        label=tr.t("password"),
        hint_text=tr.t("at_least_6_characters"),
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
        label=tr.t("confirm_password"),
        hint_text=tr.t("confirm_your_password"),
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
        tr.t("sign_in"),
        icon=ft.Icons.ARROW_FORWARD,
        width=320,
        height=48,
        color=ft.Colors.BLACK,
        bgcolor=ACCENT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
    )
    switch_prompt = ft.Text(tr.t("new_here"), size=13, color=ft.Colors.GREY_400)
    switch_button = ft.TextButton(tr.t("create_an_account"))
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
            submit_button.content = tr.t("creating_account") if registering["value"] else tr.t("signing_in")
            submit_button.icon = None
        elif not signed_in["value"]:
            submit_button.content = tr.t("create_account") if registering["value"] else tr.t("sign_in")
            submit_button.icon = ft.Icons.ARROW_FORWARD

    def apply_mode():
        hide_status()
        confirm.visible = registering["value"]
        confirm.value = ""
        if registering["value"]:
            heading.value = tr.t("create_your_account")
            subtitle.value = tr.t("username_and_password_are_enough_to_start")
            submit_button.content = tr.t("create_account")
            switch_prompt.value = tr.t("already_have_an_account")
            switch_button.content = tr.t("sign_in")
            password.autofill_hints = [ft.AutofillHint.NEW_PASSWORD]
        else:
            heading.value = tr.t("welcome_back")
            subtitle.value = tr.t("sign_in_to_keep_your_prs_and_workouts")
            submit_button.content = tr.t("sign_in")
            switch_prompt.value = tr.t("new_here")
            switch_button.content = tr.t("create_an_account")
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
            return (tr.t("enter_username_and_password"))
        if len(name) < 3:
            return (tr.t("username_min_length"))
        if len(secret) < 6:
            return (tr.t("password_min_length"))
        if registering["value"] and secret != (confirm.value or ""):
            return (tr.t("passwords_dont_match"))
        return None

    def finish(message, ok=False):
        show_status(message, ok=ok)
        if ok:
            signed_in["value"] = True
            submit_button.content = tr.t("signed_in")
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
                finish(tr.t("that_username_and_password_dont_match"))
                return
            on_success()
        except ValueError as error:
            finish(tr.t("an_error_occurred_while_processing_your_request"))
        except api_client.ApiError as error:
            finish(tr.t("an_error_occurred_while_processing_your_request"))

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
