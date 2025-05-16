import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useStudyPrograms } from "../utils/programContext";

const StudyProgram = () => {
  const [programSearchQuery, setProgramSearchQuery] = useState("");
  const [filteredPrograms, setFilteredPrograms] = useState([]);
  const { programs } = useStudyPrograms();
  const navigate = useNavigate();


  const handleProgramSearch = (query) => {
    setProgramSearchQuery(query);

    if (!query.trim()) {
      setFilteredPrograms(programs);
    } else {
      const filtered = programs.filter((program) =>
        program.name.toLowerCase().includes(query.toLowerCase()) ||
        program.degree_type.toLowerCase().includes(query.toLowerCase())
      );
      setFilteredPrograms(filtered);
    }
  };
  useEffect(() => {
    setFilteredPrograms(programs);
  }, [programs]);


  return (
    <div>
      <h1>Study Programs</h1>

      {/* Search Bar */}
      <div>
        <input
          id="programSearch"
          name="programSearch"
          type="text"
          placeholder="Search for study programs..."
          value={programSearchQuery}
          onChange={(e) => handleProgramSearch(e.target.value)}
        />
      </div>

      {/* Study Program List */}
      <div>
        {filteredPrograms.length > 0 ? (
          <ul>
            {filteredPrograms.map((program) => (
              <li
                key={program.id}
                onClick={() => navigate(`/studyprograms/${program.id}`)}
                style={{ cursor: "pointer", margin: "10px 0", textDecoration: "underline" }}
              >
                {program.name} ({program.degree_type})
              </li>
            ))}
          </ul>
        ) : (
          <p>No study programs found.</p>
        )}
      </div>
    </div>
  );
};

export default StudyProgram;
