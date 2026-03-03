from urllib.parse import quote_plus


ROLE_QUERY_ALIASES = {
    "Data Analyst": ["Data Analyst", "Business Data Analyst", "Reporting Analyst"],
    "UI/UX Designer": ["UI UX Designer", "Product Designer", "UX Designer"],
    "Backend Developer": ["Backend Developer", "Backend Engineer", "Software Engineer Backend"],
    "Frontend Developer": ["Frontend Developer", "Frontend Engineer", "UI Developer"],
    "Full Stack Developer": ["Full Stack Developer", "Software Engineer Full Stack"],
    "Data Engineer": ["Data Engineer", "ETL Engineer", "Analytics Engineer"],
    "Machine Learning Engineer": ["Machine Learning Engineer", "ML Engineer", "Applied ML Engineer"],
    "AI Engineer": ["AI Engineer", "Generative AI Engineer", "LLM Engineer"],
    "DevOps Engineer": ["DevOps Engineer", "Site Reliability Engineer", "Platform Engineer"],
    "Cloud Engineer": ["Cloud Engineer", "Cloud Infrastructure Engineer"],
    "Cyber Security Analyst": ["Cyber Security Analyst", "Security Analyst", "SOC Analyst"],
    "Business Analyst": ["Business Analyst", "Business Systems Analyst"],
    "Product Manager": ["Product Manager", "Associate Product Manager"],
    "QA Engineer": ["QA Engineer", "Test Engineer", "Automation QA Engineer"],
    "Mobile App Developer": ["Mobile App Developer", "Android Developer", "iOS Developer"],
}


LEVEL_PREFIXES = {
    "Not Job Ready": ["Trainee"],
    "Internship": ["Intern", "Trainee"],
    "Junior": ["Junior", "Associate"],
    "Mid": ["Mid Level", "Experienced"],
    "Strong Mid": ["Senior", "Lead"],
    "Senior": ["Senior", "Lead", "Principal"],
}


def get_job_queries(role, level):
    base_titles = ROLE_QUERY_ALIASES.get(role, [role])
    prefixes = LEVEL_PREFIXES.get(level, [level])

    queries = []
    for prefix in prefixes:
        for title in base_titles[:2]:
            queries.append(f"{prefix} {title}".strip())

    # Keep order, remove duplicates
    seen = set()
    deduped = []
    for query in queries:
        if query not in seen:
            seen.add(query)
            deduped.append(query)

    return deduped


def build_external_links(job_queries):
    joined_query = " OR ".join(job_queries) if job_queries else "jobs"
    encoded_query = quote_plus(joined_query)

    return {
        "linkedin": f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}",
        "indeed": f"https://www.indeed.com/jobs?q={encoded_query}",
    }
