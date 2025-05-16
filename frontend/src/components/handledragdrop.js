import { checkForConflicts, confirmWindow, processConflicts, updateConfirmedConflicts } from "../utils/checkforconflicts.js";

export const handleDragEnd = async ({
    result,
    semesters,
    setSemesters,
    searchResults,
    setSearchResults,
    setConfirmedConflicts,
    setShowConflictSummary,
    setErrorMessage,
    setSuccessMessage,
    studyplanId,
    selectedProgram,
}) => {

    // if (!result.destination) return;

    const { source, destination } = result;
    if (!result.destination) return;

    let sourceSemesterNumber = null;
    let destSemesterNumber = null;
    if (source.droppableId.startsWith("semester-")) {
        sourceSemesterNumber = parseInt(source.droppableId.substring("semester-".length));
        console.log("sourceSemesterNumber:", sourceSemesterNumber);
    }

    if (destination.droppableId.startsWith("semester-")) {
        destSemesterNumber = parseInt(destination.droppableId.substring("semester-".length));
        console.log("destSemesterNumber:", destSemesterNumber);
    }

    if (!sourceSemesterNumber && !destSemesterNumber) {
        setErrorMessage("Source or destination semester not found.");
        return;
    }


    if (source.droppableId === destination.droppableId && source.index === destination.index) {
        return;
    }


    const handleTermConflicts = async (course, destSemester, type) => {
        try {

            const { hasTermConflicts, termConflicts } = await checkForConflicts(
                course.id,
                destSemester,
                selectedProgram.id
            );

            if (hasTermConflicts) {
                const { affectedPrograms, newTermConflicts } = processConflicts(
                    termConflicts,
                    course,
                    destSemester,
                    type
                );

                const confirmMessage =
                    `Term Conflict Detected:\n\nCourse: "${course.name} (${course.courseCode})"\nFROM: "${termConflicts[0].current_term}" TO: "${destSemester.term}"\n\nConflicts in the following study programs:\n${affectedPrograms}\n\nDo you want to proceed?
                `;
                const reason = confirmWindow(confirmMessage);
                if (!reason) {
                    return { termConflictsHandled: false, newTermConflicts };

                }
                updateConfirmedConflicts(
                    newTermConflicts.map((conflict) => ({
                        ...conflict,
                        message: `"${selectedProgram.name}": ${conflict.course.name} (${conflict.course.courseCode}) was moved from "${conflict.current_term}" to "${conflict.new_term}". Reason: "${reason}".`,
                    })),
                    setConfirmedConflicts
                );
            }

            return { termConflictsHandled: true, newTermConflicts: [] };
        } catch (error) {
            setErrorMessage("Failed to check for conflict.");
            return { termConflictsHandled: false, newTermConflicts: [] };
        }
    };

    // drag from search to semester
    if (source.droppableId === "search-results" && destination.droppableId.startsWith("semester-")) {
        const courseToAdd = searchResults[source.index];
        // console.log("courseToAdd:", courseToAdd);

        try {
            const destSemester = semesters[destSemesterNumber];
            console.log("destSemester:", destSemester);
            if (!destSemester) return;


            const courseExists = destSemester.semester_courses.some((c) => c.id === courseToAdd.id);


            if (courseExists) {
                setErrorMessage("This course is already in the selected semester.");
                return;
            }

            const { termConflictsHandled, newTermConflicts } = await handleTermConflicts(
                courseToAdd,
                destSemester,
                "add"
            );
            if (!termConflictsHandled) return;

            updateConfirmedConflicts(newTermConflicts, setConfirmedConflicts);

            const updatedSemester = {
                ...destSemester,
                semester_courses: [...destSemester.semester_courses, courseToAdd],
            };

            setSemesters({
                ...semesters,
                [destSemesterNumber]: updatedSemester,
            });



            setSuccessMessage(`Added ${courseToAdd.courseCode} to semester ${destSemester.semester_number}`);
        } catch (error) {
            setErrorMessage(error.message);
        }
    }

    // drag from semester to semester
    if (source.droppableId.startsWith("semester-") && destination.droppableId.startsWith("semester-")) {
        const sourceSemester = semesters[sourceSemesterNumber];
        const destSemester = semesters[destSemesterNumber];

        if (!sourceSemester || !destSemester) return;


        const courseToMove = sourceSemester.semester_courses[source.index];

        if (courseToMove && courseToMove.courseCode === "VALGEMNE") {
            setErrorMessage("Valgemne cannot be moved between semesters.");
            return;
        }
        const courseExistsInDestination = destSemester.semester_courses.some(
            (course) => course.id === courseToMove.id
        );

        if (courseExistsInDestination) {
            setErrorMessage(`The course ${courseToMove.courseCode} already exists in semester ${destSemester.semester_number}.`);
            return;
        }

        try {
            const { termConflictsHandled, newTermConflicts } = await handleTermConflicts(
                courseToMove,
                destSemester,
                "move"
            );
            if (!termConflictsHandled) return;
            updateConfirmedConflicts(newTermConflicts, setConfirmedConflicts);


            const updatedSourceSemester = {
                ...sourceSemester,
                semester_courses: sourceSemester.semester_courses.filter((_, idx) => idx !== source.index),
            };

            const updatedDestSemester = {
                ...destSemester,
                semester_courses: [
                    ...destSemester.semester_courses.slice(0, destination.index),
                    courseToMove,
                    ...destSemester.semester_courses.slice(destination.index),
                ],
            };

            setSemesters({
                ...semesters,
                [sourceSemesterNumber]: updatedSourceSemester,
                [destSemesterNumber]: updatedDestSemester,
            });


        } catch (error) {
            setErrorMessage(error.message);
        }

    }
};

export default handleDragEnd;