def generate_suggestions(found_skills, target_role, role_data, all_roles):
    role_skills = role_data["skills"]

    missing_skills = []
    for skill in role_skills:
        if skill not in found_skills:
            missing_skills.append(skill)

    irrelevant_skills = []
    for skill in found_skills:
        if skill not in role_skills:
            irrelevant_skills.append(skill)

    suggestions = []

    if missing_skills:
        suggestions.append(
            f"Add these skills to your resume: {', '.join(missing_skills)}"
        )

    if irrelevant_skills:
        suggestions.append(
            f"Reduce focus on unrelated skills: {', '.join(irrelevant_skills)}"
        )


    return suggestions
