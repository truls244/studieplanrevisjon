import axios from "axios";
import { calculatedYear } from "./helpers.js";
/*

This file contains helper fetches used in more than 1 page.


*/


// Fetch all institutes
export const fetchAllInstitutes = async () => {
  try {
    const response = await axios.get("/backend/institutes/get_all");
    return response.data;
  } catch (err) {
    console.error("Error fetching institutes:", err);
    throw new Error("Failed to load institutes.");
  }
};

// eksportere te word docx.
export const exportStudyPlan = async (studyProgramId) => {
  try {
    const response = await axios.get(`/backend/exportdocx/${studyProgramId}`, {
      responseType: "blob",
    });

    // Dynamic filename from backend
    const contentDisposition = response.headers['content-disposition'];
    const filename = contentDisposition
      ? contentDisposition.split('filename=')[1].replace(/"/g, '')
      : `studyplan_${studyProgramId}.docx`;

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error("Error exporting study plan:", error);
    alert("Failed to export the study plan.");
  }
};

// search for studyprograms 
export const searchStudyPrograms = async (query) => {
  const response = await axios.get(`/backend/studyprograms/search?query=${query}`);
  return response.data;
};

export const searchCourses = async (query) => {
  const response = await axios.get(`/backend/courses/search?query=${query}`);
  return response.data;
};



export const fetchSemesterInfo = async (programId) => {
  try {
    const response = await axios.get(`/backend/studyprograms/${programId}/semester-info`);
    console.log("Semester info response:", response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching semester info:', error);
    throw error;
  }
};

export const checkStudyplan = async (programId, year) => {
  try {
    const response = await axios.get(`/backend/studyplans/check?studyprogram_id=${programId}&year=${year}`);
    return response.data;
  } catch (error) {
    console.error('Error checking study plan:', error);
    throw error;
  }
};


export const updateStudyPlan = async (studyplanId, payload) => {
  try {
    const response = await axios.put(`/backend/studyplans/${studyplanId}/updatecourses`, payload);
    return response.data;
  } catch (error) {
    console.error('Error updating study plan:', error);
    throw error;
  }
}


export const semesterinfo = async (programId, year) => {
  const response = await axios.get(`/backend/studyplans/studyprograms/${programId}/semesterinfo`);
  const semesterinfoData = response.data;

  const newSemesters = {};
  semesterinfoData.semesters.forEach((sem) => {
    const semesterNumber = sem.semester_number;
    newSemesters[semesterNumber] = {
      semester_number: sem.semester_number,
      term: sem.term,
      year: calculatedYear(year, sem.semester_number, sem.term),
      semester_courses: [],
    };
  });

  return newSemesters;
};


export const fetchCourses = async () => {
  try {
    const response = await axios.get("/backend/courses/");
    return response.data;
  } catch (error) {
    console.error("Failed to fetch courses:", error);
    return ("Failed to load courses. Please try again.");
  }
};

export const fetchStudyPrograms = async () => {
  try {
    const response = await axios.get("/backend/studyprograms/getAllStudyPrograms");
    return response.data;
  } catch (error) {
    console.error("Failed to fetch study programs:", error);
    return ("Failed to load study programs. Please try again.");
  }
};

export const fetchValgemne = async () => {
  try {
    const response = await axios.get("/backend/courses/valgemne");
    return response.data;
  } catch (error) {
    console.error("Failed to fetch valgemne:", error);
    return ("Failed to load valgemne. Please try again.");
  }
}

export const fetchAllValgemner = async () => {
  try {
    const response = await axios.get("/backend/courses/all_valgemne");
    return response.data;
  } catch (error) {
    console.error("Failed to fetch valgemne:", error);
    return ("Failed to load valgemne. Please try again.");
  }
}
export const fetchCategory = async () => {
  try {
    const response = await axios.get("/backend/courses/electivegroups");
    return response.data;
  } catch (error) {
    console.error("Failed to fetch category:", error);
    return ("Failed to load category. Please try again.");
  }
}




