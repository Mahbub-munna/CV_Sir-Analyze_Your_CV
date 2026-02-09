from scorer import calculate_score


def _normalize_score(value, max_value):
    if max_value <= 0:
        return 0.0
    return min((value / max_value) * 100.0, 100.0)


def calculate_career_readiness(resume_skills, experience_years, projects, role_data):
    role_skills = role_data.get("skills", [])
    skills_score = calculate_score(resume_skills, role_skills) if role_skills else 0.0

    experience_target_years = role_data.get("experience_target_years", 5)
    projects_target_count = role_data.get("projects_target_count", 4)

    experience_score = _normalize_score(experience_years, experience_target_years)
    projects_score = _normalize_score(projects, projects_target_count)

    education_score = float(role_data.get("education_score", 0.0))
    ats_score = float(role_data.get("ats_score", 0.0))

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
    if score < 30:
        return "Not Job Ready"
    if score < 50:
        return "Internship"
    if score < 70:
        return "Junior"
    if score < 85:
        return "Mid"
    if score < 95:
        return "Strong Mid"
    return "Senior"
