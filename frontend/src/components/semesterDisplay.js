import React from 'react';
import { useState, useEffect } from 'react';
import DroppableSemester from './DroppableSemester.js';
import { addValgemneToSemester, removeValgemneFromSemester, removeCourses } from '../utils/courseHelpers.js';
import '../styles/dragdrop.css';

const SemesterDisplay = ({
  semesterId,
  semesterNumber,
  courses,
  year,
  term,
  onAdministrerValgemner,
  readOnly = false,
  allCourses,
  semesters,
  setSemesters,
  setFormattedValgemner,
  valgemneCourse,
  setSearchTerm,
}) => {

  const [hasValgemne, setHasValgemne] = useState(false);
  const semesterTitle = `Semester ${semesterNumber}: ${year}-${term}`;
  const displayCourses = courses || [];
  const regularCourses = displayCourses.filter((course) => !course.is_elective);
  const fetchedValgemneCourse = valgemneCourse || allCourses.find((course) => course.courseCode === 'VALGEMNE');


  useEffect(() => {
    const valgemnePresent = courses.some((course) => course.courseCode === 'VALGEMNE');
    setHasValgemne(valgemnePresent);
  }, [courses]);


  const handleAddValgemne = () => {
    if (!fetchedValgemneCourse) {
      console.error("VALGEMNE course not found.");
      return;
    }

    const updatedSemesters = addValgemneToSemester(semesterNumber, semesters, fetchedValgemneCourse);
    console.log("Updated semesters after adding valgemne:", updatedSemesters);
    setSemesters(updatedSemesters);
    setHasValgemne(true);
  }

  const handleRemoveValgemne = () => {
    const updatedSemesters = removeValgemneFromSemester(semesterNumber, semesters);
    setSemesters(updatedSemesters);

    setFormattedValgemner((prev) => {
      const { [semesterNumber]: _, ...rest } = prev;
      return rest;
    });

    setHasValgemne(false);
  }

  const handleRemoveCourse = (courseId) => {
    setTimeout(() => {
      const updatedSemesters = removeCourses(semesterNumber, semesters, courseId);
      console.log("Updated semesters after removing course:", updatedSemesters);
      setSemesters(updatedSemesters);


      if (typeof setSearchTerm === 'function') {
        setSearchTerm("");
      }
    }, 0);
  };



  return (
    <div className="semester-details">
      <div className="semester-header">
        <h3>{semesterTitle}</h3>
        {!readOnly && (
          <>
            <button onClick={() => hasValgemne ? handleRemoveValgemne() : handleAddValgemne()} className="add-valgemne-button">
              {hasValgemne ? 'Remove Valgemne' : 'Add Valgemne'}
            </button>
          </>
        )}
      </div>
      <DroppableSemester
        semesterNumber={semesterNumber}
        semesterId={semesterId}
        courses={regularCourses}
        onRemove={handleRemoveCourse}
        onAdministrerValgemner={onAdministrerValgemner}
        readOnly={readOnly}
      />
      <div className="semester-credits">
        Total Credits: {regularCourses.reduce((sum, course) => sum + (course.credits || 0), 0)}
      </div>
    </div>
  );
};

export default SemesterDisplay;