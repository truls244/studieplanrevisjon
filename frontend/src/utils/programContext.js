import React, { createContext, useContext, useState, useEffect, } from "react";
import { fetchStudyPrograms } from "./fetchHelpers";

const StudyProgramsContext = createContext(null);
export const ProgramProvider = ({ children }) => {
    const [programs, setPrograms] = useState([]);


    useEffect(() => {
        const loadPrograms = async () => {
            try {
                const response = await fetchStudyPrograms();
                setPrograms(response);
            } catch (error) {
                console.error("Failed to fetch programs:", error);
                setPrograms([]); // empty array if error
            }
        };

        loadPrograms();
    }, []);

    return (
        <StudyProgramsContext.Provider value={{ programs, setPrograms }}>
            {children}
        </StudyProgramsContext.Provider>
    );
}

export const useStudyPrograms = () => {
    const context = useContext(StudyProgramsContext);
    if (!context) {
        throw new Error("must be used wiht StudyProgramsProvider");
    }
    return context;
};