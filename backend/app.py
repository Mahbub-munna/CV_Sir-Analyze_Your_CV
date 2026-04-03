from datetime import datetime, timedelta, timezone
import os
import re
import shutil
import uuid

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from career_scorer import calculate_career_readiness, classify_job_level
from jd_scorer import compare_resume_with_jd
from job_recommender import build_external_links
from resume_parser import extract_text
from roles import JOB_ROLES
from scorer import calculate_score
from skill_extractor import extract_skills


load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
MONGODB_URI = os.getenv("MONGODB_URI")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is missing in .env")
if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is missing in .env")

mongo_client = MongoClient(MONGODB_URI)
database = mongo_client["cv_sir"]
users_collection = database["users"]
users_collection.create_index("email", unique=True)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "https://ridyana.github.io",
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
# Utility
# -----------------------------------
def validate_password_strength(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise HTTPException(
            status_code=400,
            detail="Password must include at least one letter and one number",
        )


def create_access_token(payload: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload_to_encode = {**payload, "exp": expire}
    return jwt.encode(payload_to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def parse_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

    return parts[1]


def get_current_user(authorization: str | None = Header(default=None)):
    token = parse_bearer_token(authorization)

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("email")
    except JWTError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from error

    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def validate_file_type(filename: str):
    allowed_extensions = (".pdf", ".docx")
    if not filename.lower().endswith(allowed_extensions):
        raise ValueError("Only PDF and DOCX files are allowed.")


def map_user(user_document) -> UserOut:
    return UserOut(
        id=str(user_document["_id"]),
        name=user_document["name"],
        email=user_document["email"],
    )


# -----------------------------------
# AUTH ENDPOINTS
# -----------------------------------
@app.post("/auth/register", response_model=AuthResponse)
async def register(payload: RegisterRequest):
    validate_password_strength(payload.password)

    user_document = {
        "name": payload.name.strip(),
        "email": payload.email.lower(),
        "password_hash": password_context.hash(payload.password),
        "created_at": datetime.now(timezone.utc),
    }

    try:
        users_collection.insert_one(user_document)
    except DuplicateKeyError as error:
        raise HTTPException(status_code=409, detail="Email already exists") from error

    token = create_access_token({"email": user_document["email"]})
    return AuthResponse(access_token=token, token_type="bearer", user=map_user(user_document))


@app.post("/auth/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    user_document = users_collection.find_one({"email": payload.email.lower()})

    if not user_document or not password_context.verify(payload.password, user_document["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"email": user_document["email"]})
    return AuthResponse(access_token=token, token_type="bearer", user=map_user(user_document))


@app.get("/auth/me", response_model=UserOut)
async def auth_me(current_user=Depends(get_current_user)):
    return map_user(current_user)


# -----------------------------------
# ANALYZE ENDPOINT
# -----------------------------------
@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description_text: str = Form(None),
    target_role: str = Form(...),
    experience_years: float = Form(0),
    projects: int = Form(0),
    _current_user=Depends(get_current_user),
):
    try:
        validate_file_type(resume.filename)

        file_extension = os.path.splitext(resume.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        resume_path = os.path.join(UPLOAD_RESUME_DIR, unique_filename)

        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        resume_text = extract_text(resume_path)
        resume_skills = list(set(extract_skills(resume_text)))
        os.remove(resume_path)

        response = {
            "target_role": target_role,
            "resume_skills": resume_skills,
        }

        role_data = JOB_ROLES.get(target_role)

        if role_data:
            role_match_percentage = calculate_score(resume_skills, role_data)
            core_skills = role_data.get("core_skills", [])
            secondary_skills = role_data.get("secondary_skills", [])
            all_role_skills = set(core_skills + secondary_skills)

            response.update(
                {
                    "role_match_percentage": float(role_match_percentage),
                    "role_missing_skills": [s for s in all_role_skills if s not in resume_skills],
                    "role_extra_skills": [s for s in resume_skills if s not in all_role_skills],
                }
            )
        else:
            response.update(
                {
                    "role_match_percentage": 0.0,
                    "role_missing_skills": [],
                    "role_extra_skills": [],
                }
            )

        if job_description_text and job_description_text.strip():
            jd_skills = list(set(extract_skills(job_description_text)))
            jd_score, _jd_matched, jd_missing = compare_resume_with_jd(resume_skills, jd_skills)
            response.update(
                {
                    "job_description_skills": jd_skills,
                    "jd_match_percentage": float(jd_score),
                    "jd_missing_skills": jd_missing,
                    "jd_extra_skills": [s for s in resume_skills if s not in jd_skills],
                }
            )
        else:
            response.update(
                {
                    "jd_match_percentage": None,
                    "jd_missing_skills": [],
                    "jd_extra_skills": [],
                }
            )

        role_results = {}
        for role, data in JOB_ROLES.items():
            score = calculate_score(resume_skills, data)
            if score > 0:
                role_results[role] = float(score)

        response["role_matches"] = dict(sorted(role_results.items(), key=lambda x: x[1], reverse=True))

        career_profile = {}
        for role, data in JOB_ROLES.items():
            score, breakdown = calculate_career_readiness(resume_skills, experience_years, projects, data)
            career_profile[role] = {
                "score": float(score),
                "level": classify_job_level(score),
                "breakdown": breakdown,
            }

        response["career_profile"] = career_profile
        return JSONResponse(content=response)

    except ValueError as error:
        return JSONResponse(status_code=400, content={"error": str(error)})

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"error": "Backend processing failed", "message": str(error)},
        )


# -----------------------------------
# JOB RECOMMENDATION ENDPOINT
# -----------------------------------
@app.post("/job-recommendations")
async def job_recommendations(
    role: str = Form(...),
    level: str = Form(...),
    _current_user=Depends(get_current_user),
):
    try:
        links_data = build_external_links(role, level)

        return JSONResponse(
            content={
                "job_queries": links_data["job_queries"],
                "external_links": {
                    "linkedin": links_data["linkedin"],
                    "indeed": links_data["indeed"],
                },
            }
        )

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"error": "Job recommendation failed", "message": str(error)},
        )
