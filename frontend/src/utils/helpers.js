

/*

This file contains helper functions and components used in more than 1 page.

*/


import React from "react";
import Notifications from "../components/notifications.js";
// import { useAuth } from "../components/validateuser";
import axios from "axios";


//whichYear, used in studyprogramdetail and generatestudyplan for determining year.
export const determineBaseYear = (mostRecentPlan) => {
  return mostRecentPlan ? mostRecentPlan.year : new Date().getFullYear();
};


export const handleBecomeInCharge = async (studyProgramId) => {
  await axios.post(`/backend/studyprograms/becomeincharge/${studyProgramId}`)
    .then(response => {
      console.log(response)
    })
    .catch(error => {
      console.log(error)
    })

}
export const handleBecomeNotInCharge = async (studyProgramId) => {
  await axios.delete(`/backend/studyprograms/becomenotincharge/${studyProgramId}`)
    .then(response => {
      console.log(response)
    })
    .catch(error => {
      console.log(error)
    })

}

// Used in studyprogramDetails.js(With Generate button) and used in generatestudyplan.js (without generate button)
// Header func for "info at the top" of the study program detail and generate studyplan pages.
export const StudyProgramHeader = ({ studyProgram, baseYear, onGenerate, setNotificationsRef }) => (
  <div>
    <h1>Study Program: {studyProgram.name}</h1>
    <div className="header-actions">
      <Notifications
        programId={studyProgram.id}
        setNotificationsRef={setNotificationsRef}
      />
      {onGenerate && (
        <button onClick={onGenerate} className="generate-studyplan-button">
          Generate New Studyplan
        </button>
      )}
    </div>
    <div className="studyprogram-columns">
      <div className="studyprogram-column">
        <strong>Current Year:</strong> {baseYear || "N/A"}
      </div>
      <div className="studyprogram-column">
        <strong>Degree Type:</strong> {studyProgram.degree_type}
      </div>
      <div className="studyprogram-column">
        <strong>Institute:</strong> {studyProgram.institute_name}
      </div>
      {studyProgram.program_ansvarlig ?
        <div className="studyprogram-column">
          <strong>Ansvarlig:</strong> {studyProgram.program_ansvarlig.name}
        </div> :
        <div className="studyprogram-column">
          <strong>Ansvarlig:</strong><button onClick={() => handleBecomeInCharge(studyProgram.id, studyProgram)}>
            Bli Ansvarlig
          </button>
        </div>}
    </div>
  </div>
);



export const calculatedYear = (baseYear, semesterNumber, term) => {
  return parseInt(baseYear) + Math.floor((semesterNumber - 1) / 2) + (term === "V" ? 1 : 0);
};






// Used in studyprogramdetail.js for å lista opp tidligere studieplaner.
export const PreviousStudyPlans = ({ plans, latestPlanId, studyprogramId, onViewPlan, currentPlanId }) => (
  <div>
    <h2>Previous Study Plans</h2>
    {plans.length > 0 ? (
      <ul className="previous-studyplans-list">
        {plans.slice(0, 8).map((plan) => (
          <li key={plan.id} className="studyplan-list-item">
            <span className={plan.id === latestPlanId ? "current-plan" : ""}>
              Year: {plan.year} {plan.id === latestPlanId ? "(Current)" : ""}
            </span>
            <button
              onClick={() => onViewPlan(plan.id)}
              disabled={plan.id === currentPlanId}
            >
              {plan.id === currentPlanId ? "Currently Viewing" : "View"}
            </button>
          </li>
        ))}
      </ul>
    ) : (
      <p>No previous study plans found.</p>
    )}
  </div>
);




// used in valgemne.js, reuseable if needed.
// Displaying search bar and autocomplete dropdown for subjects.
export const SearchBar = ({ searchTerm, setSearchTerm, filteredCourses, onCourseSelect }) => (
  <div className="search-bar">
    <input
      type="text"
      placeholder="Search courses..."
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
    />
    {searchTerm && filteredCourses.length > 0 && (
      <ul className="autocomplete-dropdown">
        {filteredCourses.map((course) => (
          <li
            key={course.id}
            onClick={() => onCourseSelect(course)}
            className="autocomplete-item"
          >
            {course.name} ({course.courseCode})
          </li>
        ))}
      </ul>
    )}
  </div>
);

// SearchBar og filterSubjects blir brukt for valgemne (oldschool way), no drag/drop her. 
// Kan brukes plasser drag and drop kje går.


export const filterCourses = (courses, searchTerm) => {
  return courses.filter(
    (course) =>
      course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      course.courseCode.toLowerCase().includes(searchTerm.toLowerCase())
  );
};


//semesterpairs, studyprogramdetail
// Når man vil visa heila studieplanen i to og to semestre.
// 1-2, 3-4, 5-6 osv.
export const groupSemestersIntoPairs = (semesters) => {
  const pairs = [];
  for (let i = 0; i < semesters.length; i += 2) {
    pairs.push(semesters.slice(i, i + 2));
  }
  return pairs;
};


