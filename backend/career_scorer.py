from scorer import calculate_score


# -----------------------------------
# Helper: Normalize Score
# -----------------------------------
def _normalize_score(value, max_value):
    """
    Normalize value against max_value into 0–100 scale.
    Caps at 100.
    """
    if max_value <= 0:
        return 0.0

    percentage = (value / max_value) * 100.0
    return min(percentage, 100.0)


# -----------------------------------
# Career Readiness Calculator
# -----------------------------------
def calculate_career_readiness(
    resume_skills,
    experience_years,
    projects,
    role_data
):
    """
    Calculates career readiness score using weighted components:

    Skills        → 40%
    Experience    → 25%
    Projects      → 20%
    Education     → 10%
    ATS Quality   → 5%
    """

    # -----------------------------
    # 1. Skill Score (Weighted Core + Secondary)
    # -----------------------------
    skills_score = calculate_score(resume_skills, role_data)

    # -----------------------------
    # 2. Experience Score
    # -----------------------------
    experience_target_years = role_data.get("experience_target_years", 5)

    experience_score = _normalize_score(
        experience_years,
        experience_target_years
    )

    # -----------------------------
    # 3. Projects Score
    # -----------------------------
    projects_target_count = role_data.get("projects_target_count", 4)

    projects_score = _normalize_score(
        projects,
        projects_target_count
    )

    # -----------------------------
    # 4. Education & ATS (Optional Role Metadata)
    # -----------------------------
    education_score = float(role_data.get("education_score", 0.0))
    ats_score = float(role_data.get("ats_score", 0.0))

    # -----------------------------
    # 5. Final Weighted Score
    # -----------------------------
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


# -----------------------------------
# Job Level Classification
# -----------------------------------
def classify_job_level(score):
    """
    Classify job level based on overall career readiness score.
    """

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