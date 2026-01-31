from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os

from resume_parser import extract_text
from skill_extractor import extract_skills
from jd_scorer import compare_resume_with_jd
from roles import JOB_ROLES
from scorer import calculate_score

app = FastAPI()

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Upload Directory
# -----------------------------
UPLOAD_RESUME_DIR = "../uploads/resumes"
os.makedirs(UPLOAD_RESUME_DIR, exist_ok=True)

# -----------------------------
# Analyze Endpoint
# -----------------------------
@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description_text: str = Form(None),
    target_role: str = Form(...)
):
    try:
        # -------- Save Resume --------
        resume_path = os.path.join(UPLOAD_RESUME_DIR, resume.filename)
        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        # -------- Extract Resume Skills --------
        resume_text = extract_text(resume_path)
        resume_skills = list(set(extract_skills(resume_text)))

        response = {
            "target_role": target_role,
            "resume_skills": resume_skills
        }

        # =============================
        # TARGET ROLE ANALYSIS (ALWAYS)
        # =============================
        role_required_skills = list(set(
            JOB_ROLES.get(target_role, {}).get("skills", [])
        ))

        matched_role = [s for s in resume_skills if s in role_required_skills]
        role_missing_skills = [s for s in role_required_skills if s not in resume_skills]
        role_extra_skills = [s for s in resume_skills if s not in role_required_skills]

        role_match_percentage = calculate_score(resume_skills, role_required_skills)

        response.update({
            "role_match_percentage": float(role_match_percentage),
            "role_missing_skills": role_missing_skills,
            "role_extra_skills": role_extra_skills
        })

        # =============================
        # JOB DESCRIPTION ANALYSIS (OPTIONAL)
        # =============================
        if job_description_text and job_description_text.strip():
            jd_skills = list(set(extract_skills(job_description_text)))

            jd_score, jd_matched, jd_missing = compare_resume_with_jd(
                resume_skills, jd_skills
            )

            jd_extra_skills = [s for s in resume_skills if s not in jd_skills]

            response.update({
                "job_description_skills": jd_skills,
                "jd_match_percentage": float(jd_score),
                "jd_missing_skills": list(jd_missing),
                "jd_extra_skills": jd_extra_skills
            })
        else:
            # If no JD provided, be explicit
            response.update({
                "jd_match_percentage": None,
                "jd_missing_skills": [],
                "jd_extra_skills": []
            })

        # =============================
        # ROLE MATCH BREAKDOWN (CHART)
        # =============================
        role_results = {}
        for role, data in JOB_ROLES.items():
            score = calculate_score(resume_skills, data["skills"])
            if score > 0:
                role_results[role] = float(score)

        response["role_matches"] = dict(
            sorted(role_results.items(), key=lambda x: x[1], reverse=True)
        )

        print("FINAL RESPONSE:", response)
        return JSONResponse(content=response)

    except Exception as e:
        print("BACKEND ERROR:", e)
        return JSONResponse(
            status_code=500,
            content={"error": "Backend processing failed", "message": str(e)}
        )
