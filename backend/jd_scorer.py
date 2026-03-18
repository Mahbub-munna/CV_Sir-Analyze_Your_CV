def compare_resume_with_jd(resume_skills, jd_skills):
    """
    Compare resume skills against job description skills.

    Returns:
        match_percentage (float)
        matched_skills (list)
        missing_skills (list)
    """

    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    if not jd_set:
        return 0.0, [], []

    # Matched skills
    matched = list(resume_set.intersection(jd_set))

    # Missing skills
    missing = list(jd_set.difference(resume_set))

    match_percentage = round(
        (len(matched) / len(jd_set)) * 100,
        2
    )

    return match_percentage, matched, missing