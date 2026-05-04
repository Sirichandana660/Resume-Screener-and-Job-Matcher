from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import pickle
import json
import PyPDF2

from src.features.embeddings import get_embeddings
from src.features.skill_extraction import extract_skills
from src.models.matcher import match_resume_to_jobs

app = FastAPI()

# ------------------ CORS ------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ LOAD JOB DATA ------------------

jobs = pd.read_csv("data/extracted/archive/job_roles.csv")
jobs.fillna("", inplace=True)

jobs["combined"] = (
    jobs["Job Title"].astype(str) + " " +
    jobs["Category"].astype(str) + " " +
    jobs["Required Skills"].astype(str)
)

jobs["cleaned"] = jobs["combined"].str.lower()

# ------------------ LOAD EMBEDDINGS ------------------

with open("data/embeddings/job_embeddings.pkl", "rb") as f:
    job_embeddings = pickle.load(f)

# ------------------ LOAD SKILLS ------------------

with open("data/extracted/archive/skills_database.json", "r") as f:
    SKILLS_DB = json.load(f)

job_skills_list = [
    extract_skills(text, SKILLS_DB)
    for text in jobs["cleaned"]
]

# ------------------ PDF READER ------------------

def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "

        return text.strip()

    except Exception as e:
        print("PDF ERROR:", e)
        return ""


# ------------------ ROOT ------------------

@app.get("/")
def root():
    return {"message": "API running 🚀"}


# ------------------ MATCH ------------------

@app.post("/match")
async def match(
    resume_text: str = Form(None),
    target_role: str = Form(""),
    experience: int = Form(0),
    file: UploadFile = File(None)
):
    try:

        # -------- RESUME TEXT --------
        if file is not None:
            pdf_text = extract_text_from_pdf(file.file)

            if pdf_text.strip() == "":
                return {"error": "PDF could not be read"}

            resume_text = pdf_text

        if not resume_text or resume_text.strip() == "":
            return {"error": "Resume is empty"}

        # -------- EMBEDDING --------
        resume_embedding = get_embeddings([resume_text])[0]

        # -------- SKILLS --------
        resume_skills = extract_skills(resume_text, SKILLS_DB)

        print("\nEXTRACTED SKILLS:", resume_skills)

        # -------- MATCH --------
        indices, scores, explanations = match_resume_to_jobs(
            resume_embedding,
            job_embeddings,
            resume_skills,
            job_skills_list,
            jobs,
            target_role=target_role
        )

        results = []

        for idx, score, explain in zip(indices, scores, explanations):
            job = jobs.iloc[idx]

            results.append({
                "title": str(job.get("Job Title", "")),
                "skills": str(job.get("Required Skills", "")),
                "experience": int(job.get("Experience Years", 0)),
                "score": float(score),
                "matched_skills": explain
            })

        return {"matches": results}

    except Exception as e:
        return {"error": str(e)}