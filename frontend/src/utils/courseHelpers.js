

export const addValgemneToSemester = (semesterNumber, semesters, valgemneCourse) => {
    const semester = semesters[semesterNumber];
    if (!semester) {
        console.error(`Semester ${semesterNumber} not found.`);
        return semesters;
    }
    if (!valgemneCourse) {
        console.error("Valgemne course not found.");
        return semesters;
    }
    if (!semester.semester_courses) {
        semester.semester_courses = [];
    }
    const valgemneExists = semester.semester_courses.some((c) => c.courseCode === "VALGEMNE");
    if (valgemneExists) {
        console.warn(`VALGEMNE already exists in semester ${semesterNumber}.`);
        return semesters;
    }
    const updatedSemester = {
        ...semester,
        semester_courses: [...semester.semester_courses, valgemneCourse],
    }
    return {
        ...semesters,
        [semesterNumber]: updatedSemester,
    };

};

export const removeValgemneFromSemester = (semesterNumber, semesters) => {
    const semester = semesters[semesterNumber];
    if (!semester) {
        console.error(`Semester ${semesterNumber} not found.`);
        return semesters;
    }
    const updatedSemester = {
        ...semester,
        semester_courses: semester.semester_courses.filter(
            (course) => course.courseCode !== "VALGEMNE" && !course.is_elective
        ),
    };
    return {
        ...semesters,
        [semesterNumber]: updatedSemester,
    };
};

export const removeCourses = (semesterNumber, semesters, courseId) => {

    const semester = semesters[semesterNumber];
    if (!semester) {
        console.error(`Semester ${semesterNumber} not found.`);
        return semesters;
    }

    const updatedSemester = {
        ...semester,
        semester_courses: semester.semester_courses.filter((course) => course.id !== courseId),
    };

    return {
        ...semesters,
        [semesterNumber]: updatedSemester,
    };
}; 