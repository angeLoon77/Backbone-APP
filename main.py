from pathlib import Path

import flet as ft
import core as core
import workout_parser as wp
import api_client as db
import login as login_screen
import translations as tr

ICON = str(Path(__file__).resolve().parent / "assets" / "icon.png")

ACCENT = "#03a800"
SURFACE = "#121212"
FIELD_BG = "#161616"
BORDER = "#2c2c2c"
DANGER = "#ff5a5a"
MAX_WORKOUT_LENGTH = 10000


def format_weight(value):
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:g}"


def styled_field(**kwargs):
    props = {
        "border_radius": 12,
        "border_color": BORDER,
        "focused_border_color": ACCENT,
        "bgcolor": FIELD_BG,
        "cursor_color": ACCENT,
        "text_size": 15,
    }
    props.update(kwargs)
    return ft.TextField(**props)


def empty_state(icon, message):
    return ft.Column(
        [
            ft.Container(
                width=48,
                height=48,
                alignment=ft.Alignment.CENTER,
                content=ft.Icon(icon, size=32, color=ft.Colors.GREY_600),
            ),
            ft.Text(
                message,
                width=260,
                size=14,
                color=ft.Colors.GREY_500,
                text_align=ft.TextAlign.CENTER,
            ),
        ],
        tight=True,
        spacing=8,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


def fill_empty(column, icon, message):
    column.controls.clear()
    column.scroll = None
    column.alignment = ft.MainAxisAlignment.CENTER
    column.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    column.controls.append(empty_state(icon, message))


def begin_list(column):
    column.controls.clear()
    column.scroll = ft.ScrollMode.AUTO
    column.alignment = ft.MainAxisAlignment.START
    column.horizontal_alignment = ft.CrossAxisAlignment.STRETCH


def surface(**kwargs):
    return ft.Container(
        bgcolor=SURFACE,
        border=ft.Border.all(1, "#242424"),
        border_radius=16,
        **kwargs,
    )


def start_app(page: ft.Page, on_session_expired, on_logout=None):
    exercise_rows = db.get_exercises()
    valid_exercises = [name for name, group in exercise_rows]
    exercise_groups = {name: group for name, group in exercise_rows}
    prs = db.get_prs(1)
    if not isinstance(prs, dict):
        raise db.ApiError("Unexpected PR data from the server")

    page.clean()
    page.title = tr.t("app_title")
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ACCENT)
    page.padding = 0
    page.bgcolor = ft.Colors.BLACK

    banner_icon = ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=18, color=ACCENT)
    banner_text = ft.Text("", size=13, expand=True, color="#b7ebc2")
    banner = ft.Container(
        visible=False,
        margin=ft.Margin.symmetric(horizontal=16, vertical=4),
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        bgcolor="#102416",
        content=ft.Row(
            [banner_icon, banner_text],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
    )

    def notify(message, ok=True):
        banner.visible = True
        banner.bgcolor = "#102416" if ok else "#2a1212"
        banner_icon.icon = ft.Icons.CHECK_CIRCLE_OUTLINE if ok else ft.Icons.ERROR_OUTLINE
        banner_icon.color = ACCENT if ok else ft.Colors.RED_300
        banner_text.value = message
        banner_text.color = "#b7ebc2" if ok else "#ffb4b4"
        page.update()

    def ask_confirm(title, body, on_confirm):
        def confirm(e):
            page.pop_dialog()
            on_confirm()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text(title),
                content=ft.Text(body),
                actions=[
                    ft.TextButton(tr.t("cancel_button"), on_click=lambda e: page.pop_dialog()),
                    ft.TextButton(
                        tr.t("delete_button"),
                        style=ft.ButtonStyle(color=ft.Colors.RED_400),
                        on_click=confirm,
                    ),
                ],
            )
        )

    records_value = ft.Text("0", size=22, weight=ft.FontWeight.W_700)
    heaviest_value = ft.Text("—", size=22, weight=ft.FontWeight.W_700, color=ACCENT)
    heaviest_name = ft.Text("", size=12, color=ft.Colors.GREY_400)
    pr_logs = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    pr_search = styled_field(
        hint_text=tr.t("search_prs"),
        prefix_icon=ft.Icons.SEARCH,
        dense=True,
        text_size=14,
    )

    def refresh_summary():
        records_value.value = str(len(prs))
        if not prs:
            heaviest_value.value = "—"
            heaviest_name.value = " "
            return
        name, info = max(
            prs.items(),
            key=lambda item: (float(item[1]["weight"]), int(item[1]["reps"])),
        )
        heaviest_value.value = f"{format_weight(info['weight'])} kg"
        heaviest_name.value = name.title()

    def update_pr_logs():
        refresh_summary()
        pr_search.visible = bool(prs)
        if not prs:
            fill_empty(pr_logs, ft.Icons.EMOJI_EVENTS_OUTLINED, tr.t("no_pr_logged"))
            return

        query = (pr_search.value or "").strip().lower()
        rows = [
            (exercise, info)
            for exercise, info in prs.items()
            if query in exercise.lower()
        ]
        rows.sort(key=lambda item: item[0])
        if not rows:
            fill_empty(pr_logs, ft.Icons.SEARCH_OFF, tr.t("no_matches"))
            return

        begin_list(pr_logs)

        for exercise, info in rows:
            group = exercise_groups.get(exercise)
            group_label = str(group).replace("_", " ").title() if group else ""

            def delete_pr(ex_name):
                def run():
                    try:
                        core.delete_pr(ex_name, prs)
                    except db.SessionExpired:
                        on_session_expired()
                        return
                    except db.ApiError as error:
                        notify(str(error), ok=False)
                        return
                    update_pr_logs()
                    update_objectives()
                    page.update()

                ask_confirm(
                    tr.t("delete_pr_title"),
                    tr.t("delete_pr_body", exercise=ex_name.title()),
                    run,
                )

            pr_logs.controls.append(
                surface(
                    padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                    content=ft.Row(
                        [
                            ft.Container(
                                width=4,
                                height=36,
                                bgcolor=ACCENT,
                                border_radius=4,
                            ),
                            ft.Column(
                                [
                                    ft.Text(exercise.title(), size=16, weight=ft.FontWeight.W_600),
                                    ft.Text(
                                        " · ".join(
                                            part
                                            for part in (
                                                group_label,
                                                f"{format_weight(info['reps'])} {tr.t('reps_suffix')}",
                                            )
                                            if part
                                        ),
                                        size=12,
                                        color=ft.Colors.GREY_500,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Text(
                                f"{format_weight(info['weight'])} kg",
                                size=18,
                                weight=ft.FontWeight.W_700,
                                color=ACCENT,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_400,
                                tooltip=tr.t("delete_button"),
                                on_click=lambda e, name=exercise: delete_pr(name),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                )
            )

    pr_search.on_change = lambda e: (update_pr_logs(), page.update())

    exercise_field = styled_field(
        label=tr.t("exercise_label"),
        hint_text="bench press",
        prefix_icon=ft.Icons.SEARCH,
        autofocus=True,
        width=300,
    )
    weight_field = styled_field(
        label=tr.t("weight_label"),
        hint_text="60",
        prefix_icon=ft.Icons.FITNESS_CENTER,
        keyboard_type=ft.KeyboardType.NUMBER,
        width=300,
    )
    reps_field = styled_field(
        label=tr.t("reps_label"),
        hint_text="10",
        prefix_icon=ft.Icons.REPEAT,
        keyboard_type=ft.KeyboardType.NUMBER,
        width=300,
    )
    log_error = ft.Text("", size=12, color="#ffb4b4", visible=False, width=300)
    exercise_matches = ft.Column(spacing=0, tight=True)
    match_box = ft.Container(
        visible=False,
        width=300,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=12,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=exercise_matches,
    )

    def select_exercise(name):
        exercise_field.value = name
        match_box.visible = False
        log_error.visible = False
        page.update()

    def update_exercise_matches(e=None):
        query = (exercise_field.value or "").strip().lower()
        log_error.visible = False
        exercise_matches.controls.clear()
        if not query:
            match_box.visible = False
            page.update()
            return
        matches = [name for name in valid_exercises if query in name][:5]
        if matches == [query]:
            match_box.visible = False
            page.update()
            return
        for name in matches:
            group = exercise_groups.get(name)
            group_label = str(group).replace("_", " ").title() if group else ""
            exercise_matches.controls.append(
                ft.Container(
                    ink=True,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                    on_click=lambda e, picked=name: select_exercise(picked),
                    content=ft.Row(
                        [
                            ft.Text(name.title(), expand=True, size=14),
                            ft.Text(group_label, size=12, color=ft.Colors.GREY_500),
                        ]
                    ),
                )
            )
        match_box.visible = bool(matches)
        page.update()

    exercise_field.on_change = update_exercise_matches

    def save_pr(e):
        try:
            success, msg = core.log_PR(
                (exercise_field.value or "").strip().lower(),
                weight_field.value,
                reps_field.value,
                prs,
                valid_exercises,
            )
        except db.SessionExpired:
            page.pop_dialog()
            on_session_expired()
            return
        except db.ApiError as error:
            success, msg = False, str(error)

        if not success:
            log_error.value = msg
            log_error.visible = True
            page.update()
            return

        page.pop_dialog()
        exercise_field.value = ""
        weight_field.value = ""
        reps_field.value = ""
        match_box.visible = False
        update_pr_logs()
        update_objectives()
        notify(msg, ok=True)

    weight_field.on_submit = save_pr
    reps_field.on_submit = save_pr

    log_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(tr.t("tab_log_prs")),
        content=ft.Column(
            tight=True,
            spacing=12,
            width=300,
            controls=[
                exercise_field,
                match_box,
                weight_field,
                reps_field,
                log_error,
                ft.Button(
                    tr.t("save_button"),
                    icon=ft.Icons.SAVE,
                    width=300,
                    height=46,
                    color=ft.Colors.BLACK,
                    bgcolor=ACCENT,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    on_click=save_pr,
                ),
            ],
        ),
        actions=[
            ft.TextButton(tr.t("cancel_button"), on_click=lambda e: page.pop_dialog()),
        ],
    )

    def open_log_dialog(e=None):
        exercise_field.value = ""
        weight_field.value = ""
        reps_field.value = ""
        log_error.visible = False
        match_box.visible = False
        page.show_dialog(log_dialog)

    goals_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def update_objectives():
        if not prs:
            fill_empty(goals_list, ft.Icons.FLAG_OUTLINED, tr.t("no_objective"))
            return

        begin_list(goals_list)

        goals = core.next_goal_calculation(prs)
        for exercise, next_goal in sorted(goals.items()):
            current = prs[exercise]
            same_weight = float(next_goal["weight"]) == float(current["weight"])
            if same_weight:
                delta = f"+{int(next_goal['reps']) - int(current['reps'])} {tr.t('reps_suffix')}"
            else:
                delta = f"+{format_weight(float(next_goal['weight']) - float(current['weight']))} kg"

            goals_list.controls.append(
                surface(
                    padding=ft.Padding.symmetric(horizontal=16, vertical=14),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(exercise.title(), size=16, weight=ft.FontWeight.W_600, expand=True),
                                    ft.Container(
                                        bgcolor="#143318",
                                        border_radius=20,
                                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                        content=ft.Text(delta, size=12, weight=ft.FontWeight.W_600, color=ACCENT),
                                    ),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        f"{format_weight(current['weight'])} kg × {format_weight(current['reps'])}",
                                        color=ft.Colors.GREY_500,
                                    ),
                                    ft.Icon(ft.Icons.ARROW_FORWARD, size=16, color=ACCENT),
                                    ft.Text(
                                        f"{format_weight(next_goal['weight'])} kg × {format_weight(next_goal['reps'])}",
                                        weight=ft.FontWeight.W_700,
                                        color=ACCENT,
                                    ),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=8,
                    ),
                )
            )

    workout_field = styled_field(
        label=tr.t("workout_field_label"),
        hint_text=tr.t("workout_hint_example"),
        multiline=True,
        min_lines=8,
        max_lines=16,
        expand=True,
    )
    counter = ft.Text(
        tr.t("char_count", count=0, max_length=MAX_WORKOUT_LENGTH),
        size=12,
        color=ft.Colors.GREY_500,
    )

    def sync_counter(e=None):
        count = len(workout_field.value or "")
        counter.value = tr.t("char_count", count=count, max_length=MAX_WORKOUT_LENGTH)
        counter.color = DANGER if count > MAX_WORKOUT_LENGTH else ft.Colors.GREY_500
        if e is not None:
            counter.update()

    workout_field.on_change = sync_counter

    def process_pasted_workout(e):
        text = workout_field.value or ""
        if not text.strip():
            notify(tr.t("empty_workout_error"), ok=False)
            return
        if len(text) > MAX_WORKOUT_LENGTH:
            notify(tr.t("workout_too_long", max_length=MAX_WORKOUT_LENGTH), ok=False)
            return
        try:
            workout = wp.parse_any_workout(text)
        except ValueError as err:
            notify(str(err), ok=False)
            return

        core.log_workout(core.path_workouts, workout, text)
        try:
            logged_prs = core.process_workout(workout, prs, valid_exercises)
        except db.SessionExpired:
            on_session_expired()
            return
        except db.ApiError as error:
            notify(str(error), ok=False)
            return

        found_prs = [item for item in logged_prs if item["success"]]
        failed_prs = [item for item in logged_prs if not item["success"]]
        if not logged_prs:
            summary = tr.t("workout_saved")
        else:
            summary = tr.t("prs_logged", count=len(found_prs))
            if failed_prs:
                summary += tr.t("prs_failed", count=len(failed_prs))

        workout_field.value = ""
        sync_counter()
        update_pr_logs()
        update_objectives()
        update_workout_history()
        notify(summary, ok=not failed_prs)

    workout_history = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def update_workout_history():
        indexed_logs = core.get_workout_logs_with_index(core.path_workouts)
        if not indexed_logs:
            fill_empty(workout_history, ft.Icons.HISTORY, tr.t("no_workout_logged"))
            return

        begin_list(workout_history)

        for index, log in indexed_logs:
            title = log["title"] or tr.t("no_title")

            def delete_log(idx):
                def run():
                    core.delete_workout_log(core.path_workouts, idx)
                    update_workout_history()
                    page.update()

                ask_confirm(tr.t("delete_workout_title"), tr.t("delete_workout_body"), run)

            def edit_log(idx, current_text):
                edit_field = styled_field(
                    value=current_text,
                    multiline=True,
                    min_lines=8,
                    max_lines=14,
                    width=320,
                )
                edit_error = ft.Text("", size=12, color="#ffb4b4", visible=False, width=320)

                def save_edit(e):
                    new_text = edit_field.value or ""
                    try:
                        corrected_workout = wp.parse_any_workout(new_text)
                    except ValueError as err:
                        edit_error.value = str(err)
                        edit_error.visible = True
                        page.update()
                        return

                    core.edit_workout_log(core.path_workouts, idx, new_text, corrected_workout)
                    try:
                        core.process_workout(corrected_workout, prs, valid_exercises)
                    except db.SessionExpired:
                        page.pop_dialog()
                        on_session_expired()
                        return
                    except db.ApiError as error:
                        edit_error.value = str(error)
                        edit_error.visible = True
                        page.update()
                        return

                    page.pop_dialog()
                    update_pr_logs()
                    update_objectives()
                    update_workout_history()
                    page.update()

                page.show_dialog(
                    ft.AlertDialog(
                        modal=True,
                        title=ft.Text(tr.t("edit_workout_title")),
                        content=ft.Column(
                            tight=True,
                            spacing=8,
                            controls=[edit_field, edit_error],
                        ),
                        actions=[
                            ft.TextButton(tr.t("cancel_button"), on_click=lambda e: page.pop_dialog()),
                            ft.TextButton(tr.t("save_button"), on_click=save_edit),
                        ],
                    )
                )

            workout_history.controls.append(
                ft.ExpansionTile(
                    title=ft.Text(title, weight=ft.FontWeight.W_600, size=15),
                    subtitle=ft.Text(log["date"], size=12, color=ft.Colors.GREY_500),
                    bgcolor=SURFACE,
                    collapsed_bgcolor=SURFACE,
                    icon_color=ACCENT,
                    shape=ft.RoundedRectangleBorder(radius=16),
                    collapsed_shape=ft.RoundedRectangleBorder(radius=16),
                    controls_padding=ft.Padding.all(12),
                    controls=[
                        ft.Container(
                            bgcolor="#0c0c0c",
                            border_radius=12,
                            padding=12,
                            content=ft.Text(
                                log["raw_text"],
                                selectable=True,
                                size=13,
                                color=ft.Colors.GREY_300,
                            ),
                        ),
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    tooltip=tr.t("edit_workout_title"),
                                    on_click=lambda e, idx=index, text=log["raw_text"]: edit_log(idx, text),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip=tr.t("delete_button"),
                                    on_click=lambda e, idx=index: delete_log(idx),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                )
            )

    update_pr_logs()
    update_objectives()
    update_workout_history()

    def stat(value, caption):
        return surface(
            expand=True,
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            content=ft.Column([value, caption], spacing=2),
        )

    sections = [
        ft.Column(
            expand=True,
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Row(
                    [
                        stat(
                            records_value,
                            ft.Column(
                                [
                                    ft.Text(tr.t("stat_records"), size=12, color=ft.Colors.GREY_500),
                                    ft.Text(" ", size=12),
                                ],
                                spacing=2,
                            ),
                        ),
                        stat(
                            heaviest_value,
                            ft.Column(
                                [
                                    ft.Text(tr.t("stat_heaviest"), size=12, color=ft.Colors.GREY_500),
                                    heaviest_name,
                                ],
                                spacing=2,
                            ),
                        ),
                    ],
                    spacing=10,
                ),
                pr_search,
                pr_logs,
            ],
        ),
        ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[goals_list],
        ),
        ft.Column(
            expand=True,
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Text(tr.t("workout_intro"), size=13, color=ft.Colors.GREY_400),
                workout_field,
                ft.Row([counter], alignment=ft.MainAxisAlignment.END),
                ft.Row(
                    [
                        ft.Button(
                            tr.t("process_workout_button"),
                            icon=ft.Icons.PLAY_ARROW,
                            expand=True,
                            height=48,
                            color=ft.Colors.BLACK,
                            bgcolor=ACCENT,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                            on_click=process_pasted_workout,
                        )
                    ]
                ),
            ],
        ),
        ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[workout_history],
        ),
    ]

    titles = [
        tr.t("tab_your_prs"),
        tr.t("tab_next_objectives"),
        tr.t("tab_paste_workout"),
        tr.t("tab_workout_logs"),
    ]
    section_title = ft.Text(titles[0], size=22, weight=ft.FontWeight.W_700)
    body = ft.Container(expand=True, padding=16, content=sections[0])

    add_button = ft.IconButton(
        icon=ft.Icons.ADD,
        icon_color=ft.Colors.BLACK,
        bgcolor=ACCENT,
        tooltip=tr.t("tab_log_prs"),
        on_click=open_log_dialog,
    )

    nav_items = [
        (ft.Icons.EMOJI_EVENTS_OUTLINED, ft.Icons.EMOJI_EVENTS, tr.t("nav_prs")),
        (ft.Icons.FLAG_OUTLINED, ft.Icons.FLAG, tr.t("nav_goals")),
        (ft.Icons.CONTENT_PASTE, ft.Icons.CONTENT_PASTE_GO, tr.t("nav_paste")),
        (ft.Icons.HISTORY_OUTLINED, ft.Icons.HISTORY, tr.t("nav_history")),
    ]
    nav_pills = []
    nav_icons = []
    nav_labels = []

    def select_section(index):
        body.content = sections[index]
        section_title.value = titles[index]
        add_button.visible = index == 0
        banner.visible = False
        for i, (outline, filled, _) in enumerate(nav_items):
            selected = i == index
            nav_pills[i].bgcolor = "#163318" if selected else ft.Colors.TRANSPARENT
            nav_icons[i].icon = filled if selected else outline
            nav_icons[i].color = ACCENT if selected else ft.Colors.GREY_500
            nav_labels[i].color = ACCENT if selected else ft.Colors.GREY_500
        page.update()

    nav_slots = []
    for index, (outline, filled, label) in enumerate(nav_items):
        selected = index == 0
        icon = ft.Icon(
            filled if selected else outline,
            size=22,
            color=ACCENT if selected else ft.Colors.GREY_500,
        )
        caption = ft.Text(
            label,
            size=12,
            color=ACCENT if selected else ft.Colors.GREY_500,
            text_align=ft.TextAlign.CENTER,
        )
        pill = ft.Container(
            width=56,
            height=32,
            alignment=ft.Alignment.CENTER,
            border_radius=16,
            bgcolor="#163318" if selected else ft.Colors.TRANSPARENT,
            content=icon,
        )
        nav_icons.append(icon)
        nav_labels.append(caption)
        nav_pills.append(pill)
        nav_slots.append(
            ft.Container(
                expand=True,
                padding=ft.Padding.only(top=6, bottom=8),
                on_click=lambda e, idx=index: select_section(idx),
                content=ft.Column(
                    [pill, caption],
                    tight=True,
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        )

    nav = ft.Container(
        bgcolor=ft.Colors.BLACK,
        border=ft.Border(top=ft.BorderSide(1, "#1c1c1c")),
        content=ft.Row(
            nav_slots,
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    header = ft.Container(
        padding=ft.Padding.only(left=20, right=12, top=6, bottom=2),
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            "BACKBONE",
                            size=11,
                            weight=ft.FontWeight.W_700,
                            color=ACCENT,
                            style=ft.TextStyle(letter_spacing=2.4),
                        ),
                        section_title,
                    ],
                    spacing=0,
                    expand=True,
                ),
                add_button,
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    icon_color=ft.Colors.GREY_500,
                    tooltip=tr.t("sign_out"),
                    visible=on_logout is not None,
                    on_click=lambda e: on_logout(),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Column(
                expand=True,
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[header, banner, body, nav],
            ),
        )
    )


def main(page: ft.Page):
    page.title = tr.t("app_title")
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ACCENT)
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0
    page.window.width = 420
    page.window.height = 750
    page.window.min_width = 380
    page.window.min_height = 640
    page.window.icon = ICON
    page.window.resizable = True

    prefs = ft.SharedPreferences()
    token_key = "backbone.token"

    async def save_pref():
        token = db.get_token()
        if not token:
            return
        try:
            await prefs.set(token_key, token)
        except Exception:
            return

    async def clear_pref():
        try:
            await prefs.remove(token_key)
        except Exception:
            return

    def show_login(message=None, forget=True):
        if forget:
            db.forget_session()
            page.run_task(clear_pref)
        page.clean()
        login_screen.build(page, on_success=open_app, initial_message=message)

    def show_opening():
        page.clean()
        page.add(
            ft.SafeArea(
                expand=True,
                content=ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
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
                            ft.ProgressRing(color=ACCENT, width=28, height=28),
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=16,
                    ),
                ),
            )
        )

    def open_app():
        db.remember_session()
        page.run_task(save_pref)
        try:
            start_app(
                page,
                on_session_expired=lambda: show_login("Session expired, please log in again"),
                on_logout=show_login,
            )
        except db.SessionExpired:
            show_login("Session expired, please log in again")
        except db.ApiError as error:
            show_login(str(error), forget=False)

    async def boot():
        token = db.load_saved_token()
        if not token:
            try:
                stored = await prefs.get(token_key)
            except Exception:
                stored = None
            if isinstance(stored, str) and stored:
                token = stored
        if not token:
            show_login(forget=False)
            return
        db.set_token(token)
        show_opening()
        page.run_thread(open_app)

    page.run_task(boot)


if __name__ == "__main__":
    ft.run(main)
