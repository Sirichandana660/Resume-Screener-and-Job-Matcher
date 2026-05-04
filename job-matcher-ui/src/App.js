import React, { useState } from "react";
import "./App.css";

function App() {
  const [resume, setResume] = useState("");
  const [role, setRole] = useState("");
  const [experience, setExperience] = useState(0);
  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);

    const formData = new FormData();
    formData.append("resume_text", resume);
    formData.append("target_role", role);
    formData.append("experience", experience);

    if (file) {
      formData.append("file", file);
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/match", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.error) {
        alert(data.error);
        setResults([]);
      } else {
        setResults(data.matches || []);
      }
    } catch (error) {
      console.error(error);
      alert("Server error");
      setResults([]);
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h1>🚀 AI Resume Matcher</h1>
      <p className="subtitle">Smart job recommendations powered by ML</p>

      <div className="grid">

        {/* ---------- PROFILE ---------- */}
        <div className="card">
          <h2>Profile</h2>

          <textarea
            placeholder="Paste your resume..."
            value={resume}
            onChange={(e) => setResume(e.target.value)}
          />

          <input
            type="text"
            placeholder="Target Role (ML, Backend, Data, etc)"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          />

          <select
            value={experience}
            onChange={(e) => setExperience(e.target.value)}
          >
            <option value={0}>0 years</option>
            <option value={1}>1 year</option>
            <option value={2}>2 years</option>
            <option value={3}>3 years</option>
          </select>

          <div className="file-upload">
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
            />
          </div>

          <button onClick={handleSubmit}>
            {loading ? "Processing..." : "Find Jobs"}
          </button>
        </div>

        {/* ---------- MATCHES ---------- */}
        <div className="card">
          <h2 className="matches-title">Matches</h2>

          {results.length === 0 ? (
            <p style={{ color: "#94a3b8" }}>
              {loading ? "Matching jobs..." : "No results yet"}
            </p>
          ) : (
            results.map((job, index) => (
              <div key={index} className="job-card">

                <h3>{job.title}</h3>

                {/* Progress Bar */}
                <div className="score-bar">
                  <div
                    className="score-fill"
                    style={{ width: `${job.score * 100}%` }}
                  />
                </div>

                <p><strong>Score:</strong> {(job.score * 100).toFixed(1)}%</p>

                {/* Skill Tags */}
                <div className="skills">
                  {job.skills.split("|").map((skill, idx) => (
                    <span key={idx} className="skill-tag">
                      {skill}
                    </span>
                  ))}
                </div>

                <p><strong>Experience:</strong> {job.experience} years</p>

              </div>
            ))
          )}
        </div>

      </div>
    </div>
  );
}

export default App;