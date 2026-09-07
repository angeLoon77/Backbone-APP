# translator module

TRANSLATIONS = {
    "pt": {
        "app_title": "App de Musculação",
        "tab_your_prs": "Seus PRs",
        "tab_log_prs": "Registrar PR",
        "tab_next_objectives": "Próximos Objetivos",
        "tab_paste_workout": "Colar Treino",
        "tab_workout_logs": "Histórico",

        "no_pr_logged": "Você ainda não registrou nenhum PR!",
        "no_objective": "Nenhum PR registrado ainda!",
        "no_workout_logged": "Nenhum treino registrado ainda!",
        "no_title": "Sem título",

        "exercise_label": "Exercício",
        "weight_label": "Peso (kg)",
        "reps_label": "Repetições",
        "save_button": "Salvar",
        "process_workout_button": "Processar Treino",
        "workout_field_label": "Deixe-me analisar seu treino!",

        "edit_workout_title": "Editar Treino",
        "cancel_button": "Cancelar",

        "reps_suffix": "reps",

        "prs_logged": "{count} PR(s) registrado(s)!",
        "prs_failed": ", {count} falharam!",
    },
    "en": {
        "app_title": "Gym App",
        "tab_your_prs": "Your PRs",
        "tab_log_prs": "Log PR",
        "tab_next_objectives": "Next Objectives",
        "tab_paste_workout": "Paste Workout",
        "tab_workout_logs": "History",

        "no_pr_logged": "You haven't logged a PR yet!",
        "no_objective": "No Personal Best logged yet!",
        "no_workout_logged": "No workout logged yet!",
        "no_title": "No title",

        "exercise_label": "Exercise",
        "weight_label": "Weight (kg)",
        "reps_label": "Reps",
        "save_button": "Save",
        "process_workout_button": "Process Workout",
        "workout_field_label": "Let me dig through your workout!",

        "edit_workout_title": "Edit Workout",
        "cancel_button": "Cancel",

        "reps_suffix": "reps",

        "prs_logged": "{count} PR(s) logged!",
        "prs_failed": ", {count} failed!",
    },
}

CURRENT_LANG = "pt" # <--- trocar idioma aqui 


def t(key, **kwargs):
    text = TRANSLATIONS.get(CURRENT_LANG, TRANSLATIONS["pt"]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


def set_language(lang):
    global CURRENT_LANG
    if lang in TRANSLATIONS:
        CURRENT_LANG = lang