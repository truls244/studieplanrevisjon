// hooks/studyplanData.js
import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { calculatedYear } from '../utils/helpers';
import { fetchValgemne, fetchAllValgemner } from '../utils/fetchHelpers';
import '../styles/dragdrop.css';

export function useStudyPlanData(programId) {
  // const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // State for data
  const [studyProgram, setStudyProgram] = useState(null);
  const [semesters, setSemesters] = useState([]);
  const [valgemne, setValgemne] = useState({});
  const [latestStudyPlan, setLatestStudyPlan] = useState(null);
  const [allCourses, setAllCourses] = useState([]);
  const [previousStudyPlans, setPreviousStudyPlans] = useState([]);
  const [selectedPlanId, setSelectedPlanId] = useState(null);
  const [valgemneCourse, setValgemneCourse] = useState(null);

  const fetchData = useCallback(async (studyplan_id = null) => {
    setLoading(true);
    try {
      let endpoint = studyplan_id
        ? `/backend/studyplans/${studyplan_id}/completesp`
        : `/backend/studyplans/studyprograms/${programId}/fullsp`;

      const response = await axios.get(endpoint);
      const data = response.data;
      setSelectedPlanId(studyplan_id || (data.latest_plan?.id));
      if (data.all_plans) {
        setPreviousStudyPlans(data.all_plans);
      }
      const currentPlan = (studyplan_id && data) || data.latest_plan;
      if (!currentPlan) {
        setStudyProgram(data.program || null)
        setLatestStudyPlan(null);
        setLoading(false);
        return;
      }
      console.log("Current plan:", currentPlan);
      setStudyProgram(currentPlan.program);
      console.log("Study program data:", currentPlan.program);
      setLatestStudyPlan({
        id: currentPlan.id,
        year: currentPlan.year,
        studyprogram_id: currentPlan.studyprogram_id
      });
      // let fetchedValgemneCourse = null;
      // try {
      //   // fetchedValgemneCourse = await fetchAllValgemner();
      //   fetchedValgemneCourse = await fetchValgemne();
      //   // console.log(typeof(fetchedValgemneCourse))
      //   setValgemneCourse(fetchedValgemneCourse);
      //   console.log("Fetched VALGEMNE course:", fetchedValgemneCourse);
      // } catch (error) {
      //   console.error("Could not fetch VALGEMNE course:", error);
      // }

      // const updatedSemesters = {};
      // const valgemneData = {};

      // currentPlan.semesters.forEach((semester) => {
      //   const hasElectives = semester.semester_courses.some((course) => course.is_elective);

      //   if (hasElectives && fetchedValgemneCourse) {
      //     const credits = semester.semester_courses.filter(course => course.is_elective === false).reduce((sum, course) => sum + course.credits, 0)
      //     const alreadyHasValgemne = semester.semester_courses.some(
      //       (course) => course.courseCode === "VALGEMNE"
      //     );
      //     if (credits > 30) { credits = 0 }
      //     if (!alreadyHasValgemne) {
      //       // const correct_valgemne = fetchedValgemneCourse.filter(course => course.credits === 30 - credits)
      //       // console.log(correct_valgemne[0])
      //       // semester.semester_courses.push(correct_valgemne[0]);
      //     }
      //   }

      let fetchedValgemneCourse = null;
      try {
        fetchedValgemneCourse = await fetchValgemne();
        setValgemneCourse(fetchedValgemneCourse);
        console.log("Fetched VALGEMNE course:", fetchedValgemneCourse);
      } catch (error) {
        console.error("Could not fetch VALGEMNE course:", error);
      }

      const updatedSemesters = {};
      const valgemneData = {};

      currentPlan.semesters.forEach((semester) => {
        const hasElectives = semester.semester_courses.some((course) => course.is_elective);

        if (hasElectives && fetchedValgemneCourse) {
          const alreadyHasValgemne = semester.semester_courses.some(
            (course) => course.courseCode === "VALGEMNE"
          );

          if (!alreadyHasValgemne) {
            semester.semester_courses.push(fetchedValgemneCourse);
          }
        }

        valgemneData[semester.semester_number] = {};
        semester.semester_courses
          .filter((course) => course.is_elective)
          .forEach((course) => {
            const category = course.category
              ? { id: course.category.id, name: course.category.name }
              : "Uncategorized";
            if (!valgemneData[semester.semester_number][category.id]) {
              valgemneData[semester.semester_number][category.id] = [];
            }
            valgemneData[semester.semester_number][category.id].push(course);
          });

        updatedSemesters[semester.semester_number] = {
          id: semester.id,
          semester_number: semester.semester_number,
          semester_courses: semester.semester_courses,
          term: semester.term,
          year: calculatedYear(currentPlan.year, semester.semester_number, semester.term),
        };
      });

      setValgemne(valgemneData);
      setSemesters(updatedSemesters);

    } catch (err) {
      console.error("Error loading study program:", err);
      setError(err.message || "Failed to load study program data.");
      setLoading(false);

    } finally {
      setLoading(false);
    }
  }, [programId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const switchStudyPlan = useCallback((planId) => {
    fetchData(planId);
  }, [fetchData]);

  return {
    loading,
    error,
    studyProgram,
    semesters,
    setSemesters,
    valgemne,
    setValgemne,
    valgemneCourse,
    latestStudyPlan,
    allCourses,
    previousStudyPlans,
    selectedPlanId,
    refreshData: fetchData,
    switchStudyPlan,
  };
}