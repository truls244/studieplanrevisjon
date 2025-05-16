
export const createNewStudyplanPayload = (semesters, formattedValgemner) => {
    const semesterCoursesData = {};

    Object.values(semesters).forEach((semester) => {
        const semesterNumber = semester.semester_number;

        semesterCoursesData[semesterNumber] = semester.semester_courses
            .filter((course) => course.courseCode !== "VALGEMNE")
            .map((course) => ({
                course_id: course.id,
                is_elective: false,
            }));
    });


    Object.entries(formattedValgemner).forEach(([semesterNumber, categories]) => {
        if (!semesterCoursesData[semesterNumber]) {
            semesterCoursesData[semesterNumber] = [];
        }

        Object.values(categories).forEach((courses) => {
            semesterCoursesData[semesterNumber].push(...courses);
        });
    });

    return semesterCoursesData;
};

export const updateStudyPlanPayload = (studyPlanId, semesters, formattedValgemner) => {
    const semesterCoursesData = {};

    Object.values(semesters).forEach((semester) => {
        const semesterNumber = semester.semester_number;

        semesterCoursesData[semesterNumber] = semester.semester_courses
            .filter((course) => course.courseCode !== "VALGEMNE")
            .map((course) => ({
                course_id: course.id,
                is_elective: course.is_elective || false,
                category_id: course.category?.id || null,
            }));
    });

    Object.entries(formattedValgemner).forEach(([semesterNumber, categories]) => {
        if (!semesterCoursesData[semesterNumber]) {
            semesterCoursesData[semesterNumber] = [];
        }

        Object.values(categories).forEach((courses) => {
            courses.forEach((course) => {
                const isDuplicate = semesterCoursesData[semesterNumber].some(
                    (existingCourse) => existingCourse.course_id === course.course_id
                );
                if (!isDuplicate) {
                    semesterCoursesData[semesterNumber].push(course);
                }
            });
        });
    });

    Object.keys(semesters).forEach((semesterNumber) => {
        if (!semesterCoursesData[semesterNumber]) {
            semesterCoursesData[semesterNumber] = [];
        }
    });

    return {
        studyplan_id: studyPlanId,
        semester_courses: semesterCoursesData,

    };
};


export const generateStudyPlanPayload = (semesters, formattedValgemner = {}) => {
    const semesterCoursesData = {};
    Object.values(semesters).forEach((semester) => {
        const semesterNumber = semester.semester_number;

        semesterCoursesData[semesterNumber] = semester.semester_courses
            .filter((course) => course.courseCode !== "VALGEMNE")
            .map((course) => ({
                course_id: course.id,
                is_elective: course.is_elective || false,
                category_id: course.category?.id || null,
            }));
    });

    Object.entries(formattedValgemner).forEach(([semesterNumber, categories]) => {
        if (!semesterCoursesData[semesterNumber]) {
            semesterCoursesData[semesterNumber] = [];
        }

        Object.values(categories).forEach((courses) => {
            courses.forEach((course) => {
                const isDuplicate = semesterCoursesData[semesterNumber].some(
                    (existingCourse) => existingCourse.course_id === course.course_id
                );
                if (!isDuplicate) {
                    semesterCoursesData[semesterNumber].push(course);
                }
            });
        });
    });

    Object.keys(semesters).forEach((semesterNumber) => {
        if (!semesterCoursesData[semesterNumber]) {
            semesterCoursesData[semesterNumber] = [];
        }
    });

    return semesterCoursesData;
};
