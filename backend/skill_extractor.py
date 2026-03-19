import re
from roles import JOB_ROLES


# -----------------------------------
# Build Master Skill List Dynamically
# -----------------------------------

def _build_master_skill_list():
    skills = set()

    for role_data in JOB_ROLES.values():
        core = role_data.get("core_skills", [])
        secondary = role_data.get("secondary_skills", [])

        skills.update(core)
        skills.update(secondary)

    return list(skills)


ALL_SKILLS = _build_master_skill_list()


# -----------------------------------
# Skill Extraction Engine
# -----------------------------------

def extract_skills(text: str):
    """
    Extract known skills using word-boundary regex.
    """

    text = text.lower()
    found_skills = set()

    for skill in ALL_SKILLS:
        escaped_skill = re.escape(skill.lower())
        pattern = r"\b" + escaped_skill + r"\b"

        if re.search(pattern, text):
            found_skills.add(skill)

    return list(found_skills)