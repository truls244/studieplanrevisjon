import axios from "axios";

export const checkForConflicts = async (courseId, destSemester, studyprogramId) => {
    try {
        const response = await axios.get(`/backend/studyplans/courses/${courseId}/term-conflicts`, {
            params: {
                // semester_number: destSemester,
                // studyplan_id: studyplanId,
                new_term: destSemester.term,
                studyprogram_id: studyprogramId,
            },
        });

        console.log("Conflict check response:", response.data);

        const { has_conflicts, termConflicts } = response.data;

        return { hasTermConflicts: has_conflicts, termConflicts };
    } catch (error) {
        console.error("Error checking conflicts:", error);
        throw new Error("Failed to check for conflicts.");
    }
};



export const processConflicts = (termConflicts, course, destSemester, type) => {

    const affectedPrograms = termConflicts
        .map((c) => `- ${c.program_name} (Term: ${c.current_term})`)
        .join("\n");

    const newTermConflicts = termConflicts.map((c) => ({
        course,
        affectedProgram: {
            id: c.program_id,
            name: c.program_name,
        },
        current_term: c.current_term,
        new_term: destSemester.term,
        semesterId: destSemester.id,
        semesterNumber: destSemester.semester_number,
        type,
    }));

    return { affectedPrograms, newTermConflicts };
};


export const confirmWindow = (message) => {
    const reason = prompt(`${message}\n\nPlease provide a reason for change:`);
    if (reason === null || reason.trim() === "") {

        return null;
    }
    return reason.trim();
}

export const updateConfirmedConflicts = (newTermConflicts, setConfirmedConflicts) => {
    setConfirmedConflicts((prev) => {
        const updatedConflicts = [...prev, ...newTermConflicts];
        console.log("Updated confirmed conflicts:", updatedConflicts);
        return updatedConflicts;
    });
};