import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.features.skill_extraction import compute_skill_score

# ------------------ LOAD MODEL ------------------

try:
    with open("data/models/ranker.pkl", "rb") as f:
        ranker = pickle.load(f)
except:
    ranker = None


# ------------------ ROLE BOOST ------------------

def role_match_score(target_role, job_title):
    if not target_role:
        return 1.0

    target_role = target_role.lower()
    job_title = job_title.lower()

    if target_role in job_title:
        return 1.2

    if any(word in job_title for word in target_role.split()):
        return 1.05

    return 0.9


# ------------------ MAIN FUNCTION ------------------

def match_resume_to_jobs(
    resume_embedding,
    job_embeddings,
    resume_skills,
    job_skills_list,
    jobs_df,
    target_role=None,
    top_k=5
):

    similarities = cosine_similarity([resume_embedding], job_embeddings)[0]

    results = []

    for i, sim in enumerate(similarities):

        job = jobs_df.iloc[i]
        job_title = str(job.get("Job Title", ""))

        # ROLE SCORE
        role_score = role_match_score(target_role, job_title)

        # SKILL SCORE
        job_skills = job_skills_list[i]
        overlap = list(set(resume_skills) & set(job_skills))

        skill_score = compute_skill_score(resume_skills, job_skills)

        if skill_score == 0:
            skill_score = 0.2

        # EXPERIENCE
        job_exp = job.get("Experience Years", 0)
        exp_diff = abs(job_exp - 1)

        # ML SCORE
        features = [[sim, skill_score, exp_diff]]

        if ranker:
            try:
                ml_score = ranker.predict_proba(features)[0][1]
            except:
                ml_score = sim
        else:
            ml_score = sim

        # FINAL SCORE
        final_score = (
            0.5 * skill_score +
            0.3 * sim +
            0.2 * ml_score
        ) * role_score

        results.append({
            "index": i,
            "score": final_score,
            "overlap": overlap[:5]
        })

    # SORT
    results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

    indices = [r["index"] for r in results]
    scores = [float(r["score"]) for r in results]
    explanations = [r["overlap"] for r in results]

    return indices, scores, explanations