import React, { createContext, useContext, useState, useEffect } from "react";
import { fetchCourses } from "../utils/fetchHelpers";

const CoursesContext = createContext(null);

export const CoursesProvider = ({ children }) => {
    const [courses, setCourses] = useState([]);

    useEffect(() => {
        const loadCourses = async () => {
            try {
                const response = await fetchCourses();
                setCourses(response);
            } catch (error) {
                console.error("Failed to fetch courses:", error);
                setCourses([]); // empty array if error
            }
        };

        loadCourses();
    }, []);


    return (
        <CoursesContext.Provider value={{ courses, setCourses }}>
            {children}
        </CoursesContext.Provider>
    );
};

export const useCourses = () => {
    const context = useContext(CoursesContext);
    if (!context) {
        throw new Error("useCourses must be used within a CoursesProvider");
    }
    return context;
};