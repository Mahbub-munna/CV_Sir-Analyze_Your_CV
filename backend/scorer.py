def calculate_score(found_skills, role_data):
    """
    Calculate weighted role match score.

    Core skills = 70% weight
    Secondary skills = 30% weight
    """

    found_set = set(found_skills)

    core_skills = set(role_data.get("core_skills", []))
    secondary_skills = set(role_data.get("secondary_skills", []))

    # -----------------------------
    # Safety check
    # -----------------------------
    total_core = len(core_skills)
    total_secondary = len(secondary_skills)

    if total_core == 0 and total_secondary == 0:
        return 0.0

    # -----------------------------
    # Core Skill Score (70%)
    # -----------------------------
    core_matches = len(found_set.intersection(core_skills))
    core_score = (core_matches / total_core) if total_core > 0 else 0

    # -----------------------------
    # Secondary Skill Score (30%)
    # -----------------------------
    secondary_matches = len(found_set.intersection(secondary_skills))
    secondary_score = (
        (secondary_matches / total_secondary)
        if total_secondary > 0
        else 0
    )

    # -----------------------------
    # Weighted Final Score
    # -----------------------------
    final_score = (core_score * 0.7) + (secondary_score * 0.3)

    return round(final_score * 100, 2)