from src.features.embeddings import get_embeddings
from src.models.matcher import match_resume_to_jobs
import pickle
import pandas as pd
import json

jobs = pd.read_csv("data/extracted/archive/job_roles.csv")

with open("data/embeddings/job_embeddings.pkl", "rb") as f:
    job_embeddings = pickle.load(f)

with open("data/extracted/archive/skills_database.json") as f:
    SKILLS_DB = json.load(f)

job_skills_list = [
    [] for _ in range(len(jobs))
]

resume = "Python SQL Machine Learning Data Analysis"

embedding = get_embeddings([resume])[0]

indices, scores, _ = match_resume_to_jobs(
    embedding,
    job_embeddings,
    ["python", "sql", "machine learning"],
    job_skills_list,
    jobs
)

print("\nTop Matches:")
for i, s in zip(indices, scores):
    print(jobs.iloc[i]["Job Title"], round(s, 3))