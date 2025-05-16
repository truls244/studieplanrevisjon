import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { useParams, useNavigate } from "react-router-dom";
import "../styles/generatestudyplan.css";
import "../styles/dragdrop.css";
import ValgemneOverlay from "../components/valgemne.js";
import {
  StudyProgramHeader,
  determineBaseYear,
  groupSemestersIntoPairs,
  calculatedYear
} from "../utils/helpers.js";
import { useStudyPlanData } from "../hooks/studyplanData.js";
import SemesterDisplay from "../components/semesterDisplay.js";
import { DragDropContext } from "@hello-pangea/dnd";
import SearchCourses from "../components/searchCourses.js";
import ConflictSummary from '../components/conflictsummary.js';
import { handleDragEnd } from '../components/handledragdrop.js';
import { generateStudyPlanPayload } from "../utils/payloadHelpers.js";
import { useCourses } from "../utils/CoursesContext.js";

const GenerateStudyplan = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showOverlay, setShowOverlay] = useState(false);
  const [overlaySemester, setOverlaySemester] = useState(null);
  const [overlaySemesterNumber, setOverlaySemesterNumber] = useState(null);
  const { courses } = useCourses();
  const [confirmedConflicts, setConfirmedConflicts] = useState([]);
  const [showConflictSummary, setShowConflictSummary] = useState(false);
  const [formattedValgemner, setFormattedValgemner] = useState({});
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [fetchedNotifications, setFetchedNotifications] = useState([]);

  const {
    loading,
    error,
    studyProgram,
    semesters,
    setSemesters,
    valgemne,
    setValgemne,
    studyplanId,
    isEditMode,
    latestStudyPlan,
    valgemneCourse,
  } = useStudyPlanData(id);



  const baseYear = useMemo(() => determineBaseYear(latestStudyPlan), [latestStudyPlan]);
  const newYear = useMemo(() => baseYear + 1, [baseYear]);
  const semesterPairs = groupSemestersIntoPairs(Array.isArray(semesters) ? semesters : Object.values(semesters));


  useEffect(() => {
    if (latestStudyPlan && latestStudyPlan.semesters) {
      setSemesters(latestStudyPlan.semesters);
    }
  }, [latestStudyPlan, setSemesters]);

  useEffect(() => {
    console.log("Updated valgemne in parent:", valgemne);
  }, [valgemne]);


  const handleVisValgemner = (semesterId, semesterNumber) => {
    console.log("Opening ValgemneOverlayGENERATE for:", { semesterId, semesterNumber });
    setOverlaySemester(semesterId);
    setOverlaySemesterNumber(semesterNumber);
    setShowOverlay(true);
  };


  const handleSaveNewPlan = async () => {
    if (!id || !newYear) {
      alert("Missing required information for creating study plan.");
      return;
    }

    try {

      if (confirmedConflicts.length > 0 && !showConflictSummary) {
        setShowConflictSummary(true);
        return;
      }



      const semesterCoursesData = generateStudyPlanPayload(semesters, formattedValgemner);
      console.log("Generated semester courses data:", semesterCoursesData);
      const payload = {
        year: newYear,
        studyprogram_id: studyProgram.id,
        semester_courses: semesterCoursesData,
      };
      console.log("Payload for GEnerARTE study plan:", payload);
      const response = await axios.post(`/backend/studyplans/create/sp`, payload)
      console.log("Response from createStudyPlan:", response.data);
      alert("New study plan created successfully!");
      navigate(`/studyprograms/${id}`);
    } catch (error) {
      console.error("Error in study plan creation process:", error);
      alert(error.message || "Failed to create study plan.");
    }
  };

  if (loading) return <p>Loading study plan data...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!studyProgram) return <p>No study program found.</p>;

  return (
    <DragDropContext
      onDragEnd={(result) =>
        handleDragEnd({
          result,
          semesters,
          setSemesters,
          setErrorMessage,
          setSuccessMessage,
          setConfirmedConflicts,
          setShowConflictSummary,
          studyplanId,
          searchResults,
          setSearchResults,
          selectedProgram: studyProgram,

        })
      }
    >
      <div>
        <StudyProgramHeader
          studyProgram={studyProgram}
          baseYear={newYear}
          setNotificationsRef={setFetchedNotifications}
        />

        <ConflictSummary
          termConflicts={confirmedConflicts}
          isOpen={showConflictSummary}
          onClose={() => setShowConflictSummary(false)}
          onConfirm={() => {
            setShowConflictSummary(false);
            handleSaveNewPlan();

          }}
          onCancel={() => setShowConflictSummary(false)}
          sourceProgram={studyProgram}
          fetchedNotifications={fetchedNotifications}
        />



        <div className="edit-toolbar">
          <SearchCourses
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            maxResults={10}
            onResultsChange={setSearchResults}
            allCourses={courses}
            semesters={semesters}
          />
        </div>


        <div className="semesters-section">
          <h2>Semester Overview</h2>

          <div className="semester-columns-container">
            {semesterPairs.map((pair, pairIndex) => (
              <div key={pairIndex} className="semester-pair">
                {pair.map(semester => (
                  <div key={`semester-${semester.semester_number}`} className="semester-box">
                    <SemesterDisplay
                      semesterId={semester.id}
                      semesterNumber={semester.semester_number}
                      courses={semester.semester_courses}
                      year={calculatedYear(newYear, semester.semester_number, semester.term)}
                      term={semester.term}
                      onAdministrerValgemner={() => handleVisValgemner(semester.id, semester.semester_number)}
                      readOnly={isEditMode}
                      semesters={semesters}
                      setSemesters={setSemesters}
                      setFormattedValgemner={setFormattedValgemner}
                      valgemneCourse={valgemneCourse}
                      setSearchTerm={setSearchTerm}
                    />
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        <ValgemneOverlay
          isOpen={showOverlay}
          closeOverlay={() => setShowOverlay(false)}
          semester={overlaySemesterNumber}
          semesterNumber={overlaySemesterNumber}
          valgemne={valgemne}
          setValgemne={setValgemne}
          setFormattedValgemner={setFormattedValgemner}
          allCourses={courses}
          readOnly={false}
        />

        <div className="action-buttons">
          <button
            onClick={() => navigate(`backend/studyprograms/${id}`)}
            className="cancel-button"
          >
            Cancel
          </button>
          <button
            onClick={handleSaveNewPlan}
            className="save-button"
          >
            Generate New Study Plan
          </button>
        </div>
      </div>
    </DragDropContext>
  );
};

export default GenerateStudyplan;