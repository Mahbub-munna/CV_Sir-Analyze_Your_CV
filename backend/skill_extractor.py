DATA_ANALYST_SKILLS = [
    # Programming & Query
    "sql",
    "python",
    "r",

    # Data Analysis Libraries
    "pandas",
    "numpy",

    # Statistics & Analysis
    "statistics",
    "probability",
    "hypothesis testing",
    "regression",
    "a/b testing",

    # Data Visualization
    "excel",
    "power bi",
    "tableau",
    "matplotlib",
    "seaborn",

    # Data Handling
    "data cleaning",
    "data wrangling",
    "data preprocessing",

    # Business & Analytics
    "business analysis",
    "kpi",
    "dashboard",
    "reporting",

    # Databases
    "mysql",
    "postgresql"
]


UIUX_SKILLS = [
    # Design Tools
    "figma",
    "adobe xd",
    "sketch",
    "invision",
    "zeplin",

    # UX Process
    "user research",
    "user interviews",
    "usability testing",
    "persona creation",
    "user journey",
    "information architecture",

    # UI Design
    "ui design",
    "visual design",
    "layout design",
    "color theory",
    "typography",

    # Wireframing & Prototyping
    "wireframing",
    "low fidelity wireframes",
    "high fidelity wireframes",
    "prototyping",
    "interactive prototypes",

    # UX Principles
    "ux design",
    "design thinking",
    "human centered design",
    "accessibility",
    "wcag",

    # Design Systems
    "design system",
    "component library",
    "style guide",

    # Collaboration & Handoff
    "developer handoff",
    "design documentation",
    "agile",
    "scrum",

    # Frontend Awareness (Optional but Valuable)
    "html",
    "css",
    "responsive design",

    # Research & Testing Tools
    "hotjar",
    "maze",
    "user testing",

    # Portfolio & Presentation
    "case study",
    "portfolio",
    "storytelling"
]


def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in DATA_ANALYST_SKILLS + UIUX_SKILLS:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))
