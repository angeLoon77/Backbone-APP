import flet as ft
import main as mn
import exercises as es

def main(page: ft.Page):
    valid_exercises = es.list_exercises_en()
    data = mn.load_data(mn.path_data)
    prs = data.get("prs",{})

    page.title = "Gym App Prototype"

    pr_logs = ft.Column()

    def update_pr_logs():
        pr_logs.controls.clear()
        if not prs:
            pr_logs.controls.append(ft.Text("You Havent logged a PR yet!"))
        else:
            for exercise, info in prs.items():
                pr_logs.controls.append(ft.Text(f"{exercise.title()}: {info['weight']}kg {info['reps']}x "))

    exercise_field = ft.AutoComplete(value="", suggestions=[ft.AutoCompleteSuggestion(key=ex, value= ex) for ex in valid_exercises],
                                     on_select=lambda e: None,)
    weight_field = ft.TextField(label="Weight (kg)", width=300)
    reps_field = ft.TextField(label="Reps", width=300)
    message_log = ft.Text()

    def save_pr(e):
        success, msg = mn.log_PR(
            exercise_field.value.strip().lower(),
            weight_field.value,
            reps_field.value,
            prs,
            valid_exercises,
        )

        message_log.value = msg
        message_log.color = ft.Colors.GREEN if success else ft.Colors.RED

        if success:
            data["prs"] = prs
            mn.save_data(mn.path_data, data)
            update_pr_logs()
            update_objectives()
            exercise_field.value = ""
            weight_field.value = ""
            reps_field.value = ""

        page.update()

    goals_list = ft.Column()

    def update_objectives():
        goals_list.controls.clear()
        if not prs:
            goals_list.controls.append(ft. Text("No Personal Best Logged yet!"))
        else:
            goals = mn.next_goal_calculation(prs)
            for exercise, next_goal in goals.items():
                goals_list.controls.append(ft.Text(f"Your next Goal on: {exercise.title()} is {next_goal['weight']}kg and {next_goal['reps']} reps "))

    update_pr_logs()
    update_objectives()

    tabs_bar = ft.TabBar(
        tabs=[
            ft.Tab(label="Your PRs"),
            ft.Tab(label="Log PR"),
            ft.Tab(label="Next Objectives"),
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
                    ft.ElevatedButton("Save", on_click=save_pr),
                    message_log,
                ]),
                padding=20,
            ),
            ft.Container(content=goals_list, padding=20),
        ],
    )

    tabs = ft.Tabs(
        selected_index=0,
        length=3,
        expand=True,
        content=ft.Column(expand=True, controls=[tabs_bar, tabs_view]),
    )

    page.add(tabs)

ft.app(target=main) 