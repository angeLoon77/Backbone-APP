import flet as ft
import main as mn
import workout_parser as wp
import exercises as es

def main(page: ft.Page):
    valid_exercises = mn.list_exercises_en()
    data = mn.load_data(mn.path_data)
    prs = data.get("prs", {})

    page.title = "Gym App Prototype"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.DEEP_ORANGE)
    page.window.width = 420
    page.window.height = 750
    page.padding = 0
    page.bgcolor = ft.Colors.BLACK

    pr_logs = ft.Column(spacing=10)
    def update_pr_logs():
        pr_logs.controls.clear()
        if not prs:
            pr_logs.controls.append(ft.Text("You Havent logged a PR yet!", italic=True, color=ft.Colors.GREY))
        else:
            for exercise, info in prs.items():
                                pr_logs.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column([
                                        ft.Text(exercise.title(), weight=ft.FontWeight.BOLD, size=16),
                                        ft.Text(f"{info['reps']} reps", color=ft.Colors.GREY),
                                    ]),
                                    ft.Text(f"{info['weight']}kg", size=20, weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.DEEP_ORANGE_300),
                                ],
                            ),
                        ),
                    )
                )


    exercise_field = ft.AutoComplete(value="", suggestions=[ft.AutoCompleteSuggestion(key=ex, value= ex) for ex in valid_exercises],
                                     on_select=lambda e: None,)
    weight_field = ft.TextField(label="Weight (kg)", width=300, border_radius=10, prefix_icon=ft.Icons.FITNESS_CENTER)
    reps_field = ft.TextField(label="Reps", width=300, border_radius=10, prefix_icon=ft.Icons.REPEAT)

    def save_pr(e):
        success, msg = mn.log_PR(
            exercise_field.value.strip().lower(),
            weight_field.value,
            reps_field.value,
            prs,
            valid_exercises,
        )

        page.show_dialog(
        ft.SnackBar(
        content=ft.Text(msg),
        bgcolor=ft.Colors.GREEN_700 if success else ft.Colors.RED_700,
    )
)

        if success:
            data["prs"] = prs
            mn.save_data(mn.path_data, data)
            update_pr_logs()
            update_objectives()
            exercise_field.value = ""
            weight_field.value = ""
            reps_field.value = ""

        page.update()

    goals_list = ft.Column(spacing=10)

    def update_objectives():
        goals_list.controls.clear()
        if not prs:
            goals_list.controls.append(ft. Text("No Personal Best Logged yet!", italic=True, color=ft.Colors.GREY))
        else:
            goals = mn.next_goal_calculation(prs)
            for exercise, next_goal in goals.items():
                goals_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(exercise.title(), weight=ft.FontWeight.BOLD, size=16),
                                    ft.Text(
                                        f"{next_goal['weight']}kg x {next_goal['reps']}",
                                        color=ft.Colors.DEEP_ORANGE_300, weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                        ),
                    )
                )
    workout_field = ft.TextField(
    label="Let me Dig through your Workout!",
    multiline=True,
    min_lines=10,
    max_lines=20,
    width=380,
    border_radius=10,
    )
    def process_pasted_workout(e):
        text = workout_field.value

        try:
            workout = wp.parse_workout(text)
        except ValueError as err:
            page.show_dialog(
                ft.SnackBar(content=ft.Text(str(err)), bgcolor=ft.Colors.RED_700)
            )
            page.update()
            return

        mn.log_workout(mn.path_workouts, workout, text)
        logged_prs = mn.process_workout(workout, prs, valid_exercises, mn.path_data, data)

        prs_encontrados = [r for r in logged_prs if r["success"]]
        prs_falhos = [r for r in logged_prs if not r["success"]]

        resumo = f"{len(prs_encontrados)} PR(s) Logged(s)!"
        if prs_falhos:
            resumo += f", {len(prs_falhos)} Failed!"

        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(resumo),
                bgcolor=ft.Colors.GREEN_700 if not prs_falhos else ft.Colors.ORANGE_700,
            )
        )
        workout_field.value = ""


    update_pr_logs()
    update_objectives()

    tabs_bar = ft.TabBar(
        tabs=[
            ft.Tab(label="Your PRs", icon=ft.Icons.LIST_ALT),
            ft.Tab(label="Log PRs", icon=ft.Icons.ADD_CIRCLE_OUTLINE),
            ft.Tab(label="Next Objectives", icon=ft.Icons.FLAG_OUTLINED),
            ft.Tab(label="Paste Workout", icon=ft.Icons.NOTE_ADD),
        ],
    )

    tabs_view = ft.TabBarView(
        expand=True,
        controls=[
            ft.Container(content=pr_logs, padding=20),
            ft.Container(
                content=ft.Column([
                    exercise_field,
                    weight_field,
                    reps_field,
                    ft.ElevatedButton(
                         "Save",
                         icon=ft.Icons.SAVE,
                         width= 300, 
                         height=45,
                         style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                         on_click=save_pr),
                ]),
                padding=20,
            ),
            ft.Container(content=goals_list, padding=20),ft.Container(
        content=ft.Column(
        spacing=15,
        controls=[
            workout_field,
            ft.ElevatedButton(
                "Process Workout",
                icon=ft.Icons.PLAY_ARROW,
                width=380,
                height=45,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                on_click=process_pasted_workout,
            ),
        ],
    ),
    padding=20,
),
        ],
    )

    tabs = ft.Tabs(
        selected_index=0,
        length=4,
        expand=True,
        content=ft.Column(expand=True, controls=[tabs_bar, tabs_view]),
    )

    page.add(tabs)

ft.app(target=main) 