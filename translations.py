# translator module

TRANSLATIONS = {
    "pt": {
        "app_title": "BackBone",
        "tab_your_prs": "Seus PRs",
        "tab_log_prs": "Registrar PR",
        "tab_next_objectives": "Próximos Objetivos",
        "tab_paste_workout": "Colar Treino",
        "tab_workout_logs": "Histórico",
        "nav_prs": "PRs",
        "nav_goals": "Metas",
        "nav_paste": "Colar",
        "nav_history": "Histórico",
        "sign_out": "Sair",
        "search_prs": "Buscar exercício",
        "stat_records": "recordes",
        "stat_heaviest": "maior carga",
        "no_matches": "Nenhum exercício com esse nome.",
        "delete_button": "Excluir",
        "delete_pr_title": "Excluir PR",
        "delete_pr_body": "Excluir o recorde de {exercise}?",
        "delete_workout_title": "Excluir treino",
        "delete_workout_body": "Tirar este treino do histórico?",
        "workout_intro": "Cole o treino como você anota. Séries, cargas e recordes são lidos daí.",
        "char_count": "{count} / {max_length}",
        "workout_saved": "Treino salvo. Nenhum PR novo.",

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
        'workout_too_long': "O treino não pode ter mais de {max_length} caracteres!",
        "workout_hint_example": "Ex: 28/08 - treino de peito\nsupino\n10x40kg\n8x60kg - F, PR",


        "empty_workout_error": "O campo de treino não pode estar vazio!",
        "no_sets_found": "Nenhuma Serie encontrada no treino!",
        "edit_workout_title": "Editar Treino",
        "cancel_button": "Cancelar",

        "reps_suffix": "reps",

        "prs_logged": "{count} PR(s) registrado(s)!",
        "prs_failed": ", {count} falharam!",
    },
    "en": {
        "app_title": "Backbone",
        "tab_your_prs": "Your PRs",
        "tab_log_prs": "Log PR",
        "tab_next_objectives": "Next Objectives",
        "tab_paste_workout": "Paste Workout",
        "tab_workout_logs": "History",
        "nav_prs": "PRs",
        "nav_goals": "Goals",
        "nav_paste": "Paste",
        "nav_history": "History",
        "sign_out": "Sign out",
        "search_prs": "Search exercises",
        "stat_records": "records",
        "stat_heaviest": "heaviest",
        "no_matches": "No exercise matches that search.",
        "delete_button": "Delete",
        "delete_pr_title": "Delete PR",
        "delete_pr_body": "Delete the {exercise} record?",
        "delete_workout_title": "Delete workout",
        "delete_workout_body": "Remove this workout from history?",
        "workout_intro": "Paste the workout the way you write it. Sets, weights, and records are read from that text.",
        "char_count": "{count} / {max_length}",
        "workout_saved": "Workout saved. No new PRs.",

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
        "empty_workout_error": "Workout field cannot be empty!",
        "no_sets_found": "No sets found in the workout!",
        'workout_too_long': "Workout cannot exceed {max_length} characters!",
        'workout_hint_example': "Ex: 08/28 - chest day\nbench press\n10x40kg\n8x60kg - F, PR",

        
        "edit_workout_title": "Edit Workout",
        "cancel_button": "Cancel",

        "reps_suffix": "reps",

        "prs_logged": "{count} PR(s) logged!",
        "prs_failed": ", {count} failed!",
    },
}

CURRENT_LANG = "en" # <--- trocar idioma aqui pt/en


def t(key, **kwargs):
    text = TRANSLATIONS.get(CURRENT_LANG, TRANSLATIONS["pt"]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


def set_language(lang):
    global CURRENT_LANG
    if lang in TRANSLATIONS:
        CURRENT_LANG = lang