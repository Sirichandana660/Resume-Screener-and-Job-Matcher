import React from "react";
import SkillTag from "./SkillTag";

const JobCard = ({ job }) => {
  const score = Math.round(job.score * 100);

  return (
    <div className="job-card">
      <h3>{job["Job Title"]}</h3>

      <div className="score-bar">
        <div className="score-fill" style={{ width: `${score}%` }} />
      </div>

      <p className="score">Match Score: {score}%</p>

      <div className="skills">
        {(job["Required Skills"] || "").split("|").map((s, i) => (
          <SkillTag key={i} skill={s} />
        ))}
      </div>

      <p>🎓 {job["Education Requirement"] || "N/A"}</p>
      <p>💼 {job["Experience Years"] || 0} years</p>
    </div>
  );
};

export default JobCard;