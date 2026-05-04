import re

# ------------------ NORMALIZATION ------------------

def normalize(text):
    return text.lower().strip()


# ------------------ EXTRACT SKILLS ------------------

def extract_skills(text, skills_db):
    text = normalize(text)

    found_skills = set()

    # check each category
    for category, skills in skills_db.items():
        for skill in skills:

            skill_norm = skill.lower()

            # match whole words OR partial (important for things like "machine learning")
            if re.search(rf"\b{re.escape(skill_norm)}\b", text):
                found_skills.add(skill_norm)

            # fallback: partial match (for messy resumes)
            elif skill_norm in text:
                found_skills.add(skill_norm)

    return list(found_skills)


# ------------------ SKILL SCORE ------------------

def compute_skill_score(resume_skills, job_skills):
    if not resume_skills or not job_skills:
        return 0.0

    resume_set = set([s.lower() for s in resume_skills])
    job_set = set([s.lower() for s in job_skills])

    intersection = resume_set.intersection(job_set)
    union = resume_set.union(job_set)

    if len(union) == 0:
        return 0.0

    return len(intersection) / len(union)