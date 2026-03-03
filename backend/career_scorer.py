from scorer import calculate_score


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_score(value, max_value):
    numeric_value = max(_safe_float(value, 0.0), 0.0)
    numeric_max = _safe_float(max_value, 0.0)

    if numeric_max <= 0:
        return 0.0

    return min((numeric_value / numeric_max) * 100.0, 100.0)


def calculate_career_readiness(resume_skills, experience_years, projects, role_data):
    role_data = role_data or {}
    role_skills = role_data.get("skills", [])
    skills_score = calculate_score(resume_skills or [], role_skills)

    experience_target_years = role_data.get("experience_target_years", 5)
    projects_target_count = role_data.get("projects_target_count", 4)

    experience_score = _normalize_score(experience_years, experience_target_years)
    projects_score = _normalize_score(projects, projects_target_count)

    education_score = min(max(_safe_float(role_data.get("education_score", 0.0)), 0.0), 100.0)
    ats_score = min(max(_safe_float(role_data.get("ats_score", 0.0)), 0.0), 100.0)

    overall_score = round(
        (skills_score * 0.40)
        + (experience_score * 0.25)
        + (projects_score * 0.20)
        + (education_score * 0.10)
        + (ats_score * 0.05),
        2,
    )

    breakdown = {
        "skills_score": round(skills_score, 2),
        "experience_score": round(experience_score, 2),
        "projects_score": round(projects_score, 2),
        "education_score": round(education_score, 2),
        "ats_score": round(ats_score, 2),
    }

    return overall_score, breakdown


def classify_job_level(score):
    numeric_score = _safe_float(score, 0.0)

    if numeric_score < 30:
        return "Not Job Ready"
    if numeric_score < 50:
        return "Internship"
    if numeric_score < 70:
        return "Junior"
    if numeric_score < 85:
        return "Mid"
    if numeric_score < 95:
        return "Strong Mid"
    return "Senior"
