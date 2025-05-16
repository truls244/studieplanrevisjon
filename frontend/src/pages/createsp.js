// src/pages/createsp.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";
import { DragDropContext } from "@hello-pangea/dnd";
import "../styles/dragdrop.css";
import "../styles/createsp.css";
import ValgemneOverlay from '../components/valgemne.js';
import Notifications from "../components/notifications.js";
import SemesterDisplay from '../components/semesterDisplay.js';
import SearchCourses from '../components/searchCourses.js';
import ConflictSummary from '../components/conflictsummary.js';
import { handleDragEnd } from '../components/handledragdrop.js';
import { groupSemestersIntoPairs } from '../utils/helpers.js';
import { checkStudyplan, semesterinfo, fetchSemesterInfo } from "../utils/fetchHelpers.js";
import { createNewStudyplanPayload } from "../utils/payloadHelpers.js";
import { useCourses } from "../utils/CoursesContext.js";
import { useStudyPrograms } from "../utils/programContext.js";


const CreateSP = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const prefilledProgram = location.state?.program || null;
    const [programSearchQuery, setProgramSearchQuery] = useState(prefilledProgram?.name || "");
    const [selectedProgram, setSelectedProgram] = useState(prefilledProgram || null);
    const [filteredPrograms, setFilteredPrograms] = useState([]);
    const [year, setYear] = useState(new Date().getFullYear());
    const [isInitialized, setIsInitialized] = useState(false);
    const [studyplanId, setStudyplanId] = useState(null);
    const [searchTerm, setSearchTerm] = useState("");
    const { courses } = useCourses();
    const { programs } = useStudyPrograms();
    const [searchResults, setSearchResults] = useState([]);
    const [semesters, setSemesters] = useState({});
    const [valgemneOverlayOpen, setValgemneOverlayOpen] = useState(false);
    const [selectedSemesterId, setSelectedSemesterId] = useState(null);
    const [selectedSemesterNumber, setSelectedSemesterNumber] = useState(null);
    const [valgemne, setValgemne] = useState({});
    const [formattedValgemner, setFormattedValgemner] = useState({});
    const [confirmedConflicts, setConfirmedConflicts] = useState([]);
    const [showConflictSummary, setShowConflictSummary] = useState(false);

    const [isLoading, setIsLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [successMessage, setSuccessMessage] = useState("");

    useEffect(() => {
        if (prefilledProgram) {
            setSelectedProgram(prefilledProgram);
            setProgramSearchQuery(prefilledProgram.name);
        }
    }, [prefilledProgram]);


    const handleProgramSearch = (query) => {
        setProgramSearchQuery(query);

        if (!query.trim()) {
            setFilteredPrograms([]);
        } else {
            const filtered = programs.filter((program) =>
                program.name.toLowerCase().includes(query.toLowerCase()) ||
                program.degree_type.toLowerCase().includes(query.toLowerCase())
            );
            setFilteredPrograms(filtered);
        }
    };

    // Select a study program
    const selectProgram = (program) => {
        setSelectedProgram(program);
        setProgramSearchQuery(program.name);
        setFilteredPrograms([]);
        setErrorMessage("");
    };

    const handleAdministrerValgemner = (semesterId, semesterNumber) => {
        setValgemne((prev) => ({
            ...prev,
            [semesterNumber]: prev[semesterNumber] || {},
        }));

        setSelectedSemesterId(semesterId);
        setSelectedSemesterNumber(semesterNumber);
        setValgemneOverlayOpen(true);
    };




    const initializeStudyplan = async () => {
        if (!selectedProgram) {
            setErrorMessage("Please select a study program first.");
            return;
        }

        if (!year || year < 2000) {
            setErrorMessage("Please enter a valid year (2000 or later).");
            return;
        }

        setErrorMessage("");
        setIsLoading(true);
        console.log("Initializing study plan for:", selectedProgram, year);

        try {
            const checkResponse = await checkStudyplan(selectedProgram.id, year);
            if (checkResponse.exists) {
                setErrorMessage(`A study plan for ${selectedProgram.name} (${year}) already exists.`);
                return;
            }
            const newSemesters = await semesterinfo(selectedProgram.id, year);
            setSemesters(newSemesters);
            setIsInitialized(true);
            setSuccessMessage(`Initialized study plan for ${selectedProgram.name} (${year})`);
        } catch (error) {
            console.error("Error initializing study plan:", error);
            setErrorMessage(error.response?.data?.error || "Failed to initialize study plan. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };


    const saveStudyplan = async () => {
        if (!selectedProgram || !year || !isInitialized || semesters.length === 0) {
            setErrorMessage("Please initialize the study plan first.");
            return;
        }

        if (confirmedConflicts.length > 0 && !showConflictSummary) {
            setShowConflictSummary(true);
            return;
        }
        setIsLoading(true);
        setErrorMessage("");


        try {

            const structureResponse = await fetchSemesterInfo(selectedProgram.id);
            const semesterinfoData = structureResponse.data;
            const semesterCoursesData = createNewStudyplanPayload(semesters, formattedValgemner, semesterinfoData);

            const payload = {
                year: parseInt(year),
                studyprogram_id: selectedProgram.id,
                semester_courses: semesterCoursesData
            };
            console.log("CREATESP Payload for study plan creation:", payload);
            const response = await axios.post('/backend/studyplans/create/sp', payload);
            console.log("CREATESP Sending semester data:", semesterCoursesData);
            console.log("CreateSP study plan response:", response.data);
            setSuccessMessage("Study plan saved successfully!");
            setTimeout(() => {
                navigate(`/studyprograms/${selectedProgram.id}`);
            }, 2000);
        } catch (error) {
            console.error("Error saving study plan:", error);
            setErrorMessage(error.response?.data?.error || "Failed to save study plan. Please try again.");
        } finally {
            setIsLoading(false);
            setShowConflictSummary(false);
        }
    };


    const semesterPairs = groupSemestersIntoPairs(Array.isArray(semesters) ? semesters : Object.values(semesters));

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
                    selectedProgram,


                })
            }
        >

            <h1>Create New Study Plan</h1>
            {selectedProgram && (
                <div className="notifications-container">
                    <Notifications programId={selectedProgram.id} />
                </div>
            )}
            {errorMessage && <div className="error-message">{errorMessage}</div>}
            {successMessage && <div className="success-message">{successMessage}</div>}

            <div className="setup-section">
                <h2>Set Up Study Plan</h2>

                <div className="form-group">
                    <label>Study Program:</label>
                    <div className="search-container">
                        <input
                            type="text"
                            value={programSearchQuery}
                            onChange={(e) => handleProgramSearch(e.target.value)}
                            placeholder="Search for a study program"
                            disabled={isInitialized || isLoading}
                        />

                        {/* Show search results */}
                        {filteredPrograms.length > 0 && (
                            <ul className="search-resultsz">
                                {filteredPrograms.map(program => (
                                    <li
                                        key={program.id}
                                        onClick={() => selectProgram(program)}
                                    >
                                        {program.name} ({program.degree_type})
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>

                    {/* Display selected program */}
                    {selectedProgram && (
                        <div className="selected-program">
                            <p><strong>Selected:</strong> {selectedProgram.name} ({selectedProgram.degree_type})</p>
                        </div>
                    )}
                </div>

                <div className="form-group">
                    <label>Year:</label>
                    <input
                        type="number"
                        value={year}
                        onChange={(e) => setYear(e.target.value)}
                        min="2000"
                        disabled={isInitialized || isLoading}
                    />
                </div>

                <button
                    onClick={initializeStudyplan}
                    disabled={!selectedProgram || isInitialized || isLoading}
                    className="primary-button"
                >
                    {isLoading
                        ? "Initializing..."
                        : `Initialize Study Plan for ${selectedProgram ? selectedProgram.name : ""} (${year})`}
                </button>
            </div>

            <ConflictSummary
                termConflicts={confirmedConflicts}
                isOpen={showConflictSummary}
                onClose={() => setShowConflictSummary(false)}
                onConfirm={() => {
                    setShowConflictSummary(false);
                    saveStudyplan();
                }}
                onCancel={() => setShowConflictSummary(false)}
                sourceProgram={selectedProgram}
            />


            {isInitialized && (
                <>
                    <div className="add-courses-section">
                        <h2>Add by draggin Courses</h2>
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
                                                year={semester.year}
                                                term={semester.term}
                                                onAdministrerValgemner={() => handleAdministrerValgemner(semester.id, semester.semester_number)}
                                                readOnly={false}
                                                allCourses={courses}
                                                semesters={semesters}
                                                setFormattedValgemner={setFormattedValgemner}
                                                setSemesters={setSemesters}
                                                setSearchTerm={setSearchTerm}

                                            />
                                        </div>
                                    ))}
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="actions-section">
                        <button
                            onClick={saveStudyplan}
                            disabled={isLoading}
                            className="save-button"
                        >
                            {isLoading ? "Saving..." : "Save Study Plan"}
                        </button>
                    </div>

                    {/* ValgemneOverlay */}
                    <ValgemneOverlay
                        isOpen={valgemneOverlayOpen}
                        closeOverlay={() => setValgemneOverlayOpen(false)}
                        semester={selectedSemesterNumber}
                        semesterNumber={selectedSemesterNumber}
                        valgemne={valgemne}
                        setValgemne={setValgemne}
                        setFormattedValgemner={setFormattedValgemner}
                        allCourses={courses}
                        readOnly={false}
                    />
                </>
            )}
        </DragDropContext>
    );
};

export default CreateSP;