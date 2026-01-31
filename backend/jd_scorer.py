def compare_resume_with_jd(resume_skills, jd_skills):
    matched = []
    missing = []

    for skill in jd_skills:
        if skill in resume_skills:
            matched.append(skill)
        else:
            missing.append(skill)

    match_percentage = round(
        (len(matched) / len(jd_skills)) * 100, 2
    ) if jd_skills else 0

    return match_percentage, matched, missing
