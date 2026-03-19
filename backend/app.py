from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import uuid

from resume_parser import extract_text
from skill_extractor import extract_skills
from jd_scorer import compare_resume_with_jd
from roles import JOB_ROLES
from scorer import calculate_score
from career_scorer import calculate_career_readiness, classify_job_level
from job_recommender import build_external_links


# -----------------------------------
# FastAPI App Initialization
# -----------------------------------
app = FastAPI()


# -----------------------------------
# CORS Configuration (FIXED)
# -----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://ridyana.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------
# Upload Directory Setup
# -----------------------------------
UPLOAD_RESUME_DIR = "uploads/resumes"
os.makedirs(UPLOAD_RESUME_DIR, exist_ok=True)


# -----------------------------------
# File Validation
# -----------------------------------
def validate_file_type(filename: str):
    allowed_extensions = (".pdf", ".docx")
    if not filename.lower().endswith(allowed_extensions):
        raise ValueError("Only PDF and DOCX files are allowed.")


# -----------------------------------
# ANALYZE ENDPOINT
# -----------------------------------
@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description_text: str = Form(None),
    target_role: str = Form(...),
    experience_years: float = Form(0),
    projects: int = Form(0)
):

    try:

        # -----------------------------------
        # Validate & Save Resume
        # -----------------------------------
        validate_file_type(resume.filename)

        file_extension = os.path.splitext(resume.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        resume_path = os.path.join(UPLOAD_RESUME_DIR, unique_filename)

        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        # -----------------------------------
        # Extract Resume Text
        # -----------------------------------
        resume_text = extract_text(resume_path)
        resume_skills = list(set(extract_skills(resume_text)))

        os.remove(resume_path)

        response = {
            "target_role": target_role,
            "resume_skills": resume_skills
        }

        # -----------------------------------
        # ROLE MATCHING
        # -----------------------------------
        role_data = JOB_ROLES.get(target_role)

        if role_data:

            role_match_percentage = calculate_score(
                resume_skills,
                role_data
            )

            core_skills = role_data.get("core_skills", [])
            secondary_skills = role_data.get("secondary_skills", [])

            all_role_skills = set(core_skills + secondary_skills)

            role_missing_skills = [
                s for s in all_role_skills if s not in resume_skills
            ]

            role_extra_skills = [
                s for s in resume_skills if s not in all_role_skills
            ]

            response.update({
                "role_match_percentage": float(role_match_percentage),
                "role_missing_skills": role_missing_skills,
                "role_extra_skills": role_extra_skills
            })

        else:

            response.update({
                "role_match_percentage": 0.0,
                "role_missing_skills": [],
                "role_extra_skills": []
            })

        # -----------------------------------
        # JOB DESCRIPTION MATCHING
        # -----------------------------------
        if job_description_text and job_description_text.strip():

            jd_skills = list(set(extract_skills(job_description_text)))

            jd_score, jd_matched, jd_missing = compare_resume_with_jd(
                resume_skills,
                jd_skills
            )

            jd_extra_skills = [
                s for s in resume_skills if s not in jd_skills
            ]

            response.update({
                "job_description_skills": jd_skills,
                "jd_match_percentage": float(jd_score),
                "jd_missing_skills": jd_missing,
                "jd_extra_skills": jd_extra_skills
            })

        else:

            response.update({
                "jd_match_percentage": None,
                "jd_missing_skills": [],
                "jd_extra_skills": []
            })

        # -----------------------------------
        # ROLE RANKING CHART
        # -----------------------------------
        role_results = {}

        for role, data in JOB_ROLES.items():

            score = calculate_score(resume_skills, data)

            if score > 0:
                role_results[role] = float(score)

        response["role_matches"] = dict(
            sorted(role_results.items(), key=lambda x: x[1], reverse=True)
        )

        # -----------------------------------
        # CAREER READINESS
        # -----------------------------------
        career_profile = {}

        for role, data in JOB_ROLES.items():

            score, breakdown = calculate_career_readiness(
                resume_skills,
                experience_years,
                projects,
                data
            )

            career_profile[role] = {
                "score": float(score),
                "level": classify_job_level(score),
                "breakdown": breakdown
            }

        response["career_profile"] = career_profile

        return JSONResponse(content=response)

    except ValueError as ve:

        return JSONResponse(
            status_code=400,
            content={"error": str(ve)}
        )

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "error": "Backend processing failed",
                "message": str(e)
            }
        )


# -----------------------------------
# JOB RECOMMENDATION ENDPOINT
# -----------------------------------
@app.post("/job-recommendations")
async def job_recommendations(role: str = Form(...), level: str = Form(...)):

    try:

        links_data = build_external_links(role, level)

        return JSONResponse(content={
            "job_queries": links_data["job_queries"],
            "external_links": {
                "linkedin": links_data["linkedin"],
                "indeed": links_data["indeed"]
            }
        })

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "error": "Job recommendation failed",
                "message": str(e)
            }
        )