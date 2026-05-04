import pandas as pd
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import xgboost as xgb
import pickle

from src.data.load_data import load_data
from src.data.preprocess import preprocess_text
from src.features.skill_extraction import extract_skills, compute_skill_score


def build_dataset():
    jobs, resumes = load_data()

    # Combine + clean
    jobs['combined'] = (
        "Job Title: " + jobs['Job Title'] +
        ". Skills: " + jobs['Required Skills']
    )
    jobs['cleaned'] = jobs['combined'].apply(preprocess_text)

    resumes['combined'] = resumes['resume_text'] + " " + resumes['description']
    resumes['cleaned'] = resumes['combined'].apply(preprocess_text)

    # Load skills
    with open("data/extracted/archive/skills_database.json") as f:
        skills_db = json.load(f)

    skills_list = list(skills_db.keys())

    jobs['skills'] = jobs['cleaned'].apply(lambda x: extract_skills(x, skills_list))
    resumes['skills'] = resumes['cleaned'].apply(lambda x: extract_skills(x, skills_list))

    model = SentenceTransformer('all-mpnet-base-v2')

    job_emb = model.encode(jobs['cleaned'].tolist(), normalize_embeddings=True)
    res_emb = model.encode(resumes['cleaned'].tolist(), normalize_embeddings=True)

    X = []
    y = []

    # Create pairs
    for i, r_emb in enumerate(res_emb):
        for j, j_emb in enumerate(job_emb):

            sim = cosine_similarity([r_emb], [j_emb])[0][0]

            skill_score = compute_skill_score(
                resumes['skills'].iloc[i],
                jobs['skills'].iloc[j]
            )

            exp_diff = abs(jobs['Experience Years'].iloc[j] - 1)  # assume fresher

            features = [sim, skill_score, exp_diff]

            # Fake label
            label = 1 if sim > 0.5 else 0

            X.append(features)
            y.append(label)

    return np.array(X), np.array(y)


def train():
    print("Building dataset...")
    X, y = build_dataset()

    print("Training model...")

    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1
    )

    model.fit(X, y)

    import os
    os.makedirs("data/models", exist_ok=True)
    
    with open("data/models/ranker.pkl", "wb") as f:
        pickle.dump(model, f)

    print("Model saved ✅")


if __name__ == "__main__":
    train()