def rank_jobs(jobs_df, indices, scores):
    results = []

    for idx, score in zip(indices, scores):
        job = jobs_df.iloc[idx].to_dict()
        job['score'] = float(score)
        results.append(job)

    return results