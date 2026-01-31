def calculate_score(found_skills, role_skills):
    match_count = 0

    for skill in role_skills:
        if skill in found_skills:
            match_count += 1

    return round((match_count / len(role_skills)) * 100, 2)
