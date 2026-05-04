from src.data.load_data import load_data
from src.data.preprocess import preprocess_text
from src.features.embeddings import get_embeddings
from src.models.matcher import match_resume_to_jobs
from src.models.ranker import rank_jobs
from src.features.skill_extraction import extract_skills

import pickle
import os
import json


def main():
    print("Pipeline starting...")

    jobs, resumes = load_data()

    print("Columns:")
    print("Jobs:", jobs.columns)
    print("Resumes:", resumes.columns)

    print("Preprocessing...")

    # Combine job fields
    jobs['combined'] = (
    "Job Title: " + jobs['Job Title'] +
    ". Category: " + jobs['Category'] +
    ". Skills: " + jobs['Required Skills'] +
    ". Experience: " + jobs['Experience Years'].astype(str)
)
    jobs['cleaned'] = jobs['combined'].apply(preprocess_text)

    # Combine resume fields
    resumes['combined'] = (
        resumes['resume_text'] + " " +
        resumes['description']
    )
    resumes['cleaned'] = resumes['combined'].apply(preprocess_text)

    print("Loading skills database...")

    with open("data/extracted/archive/skills_database.json") as f:
        skills_db = json.load(f)

    skills_list = list(skills_db.keys())

    print("Extracting skills...")

    jobs['skills'] = jobs['cleaned'].apply(lambda x: extract_skills(x, skills_list))
    resumes['skills'] = resumes['cleaned'].apply(lambda x: extract_skills(x, skills_list))

    print("Filtering jobs (Technology only)...")

    jobs_filtered = jobs[jobs['Category'] == "Technology"].reset_index(drop=True)

    print("Generating embeddings...")

    job_embeddings = get_embeddings(jobs_filtered['cleaned'].tolist())
    resume_embeddings = get_embeddings(resumes['cleaned'].tolist())

    os.makedirs("data/embeddings", exist_ok=True)

    with open("data/embeddings/job_embeddings.pkl", "wb") as f:
        pickle.dump(job_embeddings, f)

    with open("data/embeddings/resume_embeddings.pkl", "wb") as f:
        pickle.dump(resume_embeddings, f)

    print("Embeddings saved ✅")

    print("\nTesting matching...")

    test_embedding = resume_embeddings[0]
    resume_skills = resumes['skills'].iloc[0]
    job_skills_list = jobs_filtered['skills'].tolist()

    indices, scores = match_resume_to_jobs(
        test_embedding,
        job_embeddings,
        resume_skills,
        job_skills_list
    )

    results = rank_jobs(jobs_filtered, indices, scores)

    print("\nTop Matches:\n")
    for r in results:
        print(f"{r['Job Title']} | Score: {r['score']:.4f}")


if __name__ == "__main__":
    main()