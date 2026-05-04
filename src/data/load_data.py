import pandas as pd

def load_data():
    jobs = pd.read_csv("data/extracted/archive/job_roles.csv")
    resumes = pd.read_json("data/extracted/archive/test_resumes.json")

    return jobs, resumes