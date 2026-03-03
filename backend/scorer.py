def calculate_score(found_skills, role_skills):
    if not role_skills:
        return 0.0

    found_set = set(found_skills or [])
    match_count = 0

    for skill in role_skills:
        if skill in found_set:
            match_count += 1

    return round((match_count / len(role_skills)) * 100, 2)
