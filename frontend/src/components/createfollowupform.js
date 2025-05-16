import React, { useState } from "react";

const CreateFollowupForm = ({ differences = [], onSave }) => {
    const [reasoning, setReasoning] = useState({}); // Store the reasoning for each subject
  
    const handleReasonChange = (subjectId, value) => {
      setReasoning((prev) => ({
        ...prev,
        [subjectId]: value,
      }));
    };
  
    const handleSubmit = (e) => {
      e.preventDefault();
  
      const invalidFields = Object.entries(reasoning).filter(
        ([_, reason]) => !reason.trim()
      );
      if (invalidFields.length > 0) {
        alert("All changes must have reasoning!");
        return;
      }
  
      onSave(reasoning);
    };


  if (!differences || differences.length === 0) {
    return <p>No changes to explain.</p>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Reasoning for Changes</h2>
      <table className="reasoning-table">
        <thead>
          <tr>
            <th>Subject</th>
            <th>Change Type</th>
            <th>Reasoning</th>
          </tr>
        </thead>
        <tbody>
          {differences.map(({ id, subject, changeType }) => (
            <tr key={id}>
              <td>{subject}</td>
              <td>{changeType}</td>
              <td>
                <textarea
                  placeholder={`Reason for ${changeType.toLowerCase()}`}
                  value={reasoning[id] || ""}
                  onChange={(e) => handleReasonChange(id, e.target.value)}
                  required
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button type="submit" className="save-button">
        Save Follow-Up
      </button>
    </form>
  );
};

export default CreateFollowupForm;
