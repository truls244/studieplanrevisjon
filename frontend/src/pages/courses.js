import React, { useState, useEffect, useCallback, use } from "react";
import "../styles/EditCourse.css";
import { Link } from "react-router-dom";
import {  useCourses } from "../utils/CoursesContext";
import FilterCourse from "../components/filtercourse";


const Courses = () => {
    const { courses }  = useCourses();
    const [filteredCourses, setFilteredCourses] = useState(courses); // filtersøk på emne
    const [searchTerm, setSearchTerm] = useState(""); // søkeord


    // søkebar input
    const handleSearch = (e) => {
        const value = e.target.value.toLowerCase();
        setSearchTerm(value);

        // Søk på navn/emnekode
        const filtered = courses.filter((course) =>
            course.name.toLowerCase().includes(value) ||
            course.courseCode.toLowerCase().includes(value)
        );
        setFilteredCourses(filtered);
    };
    

    return (
        <div className="Course-Container" >
            
            <div className="Course-List" >
                <h1>Oversikt over emner</h1>
                
                {/* Søkebar */}
                <input
                    type="text"
                    placeholder="Search by Name or Subject Code"
                    value={searchTerm}
                    onChange={handleSearch}
                    style={{ marginBottom: "20px", width: "100%", padding: "10px", fontSize: "16px" }}
                />

                {/* Emne tabell */}
                <table border="1" style={{ width: "100%", textAlign: "left" }}>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Subject Code</th>
                            <th>Semester</th>
                            <th>Credits</th>
                            <th>Is Active</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredCourses.map((course) =>
                            
                                <tr key={course.id}>
                                    <td>
                                        <Link to={`/courses/details/${course.id}`} state={{"courseid":course.id}} >{course.name}</Link>
                                    </td>
                                    <td>{course.courseCode}</td>
                                    <td>{course.semester}</td>
                                    <td>{course.credits}</td>
                                    <td>{course.is_active ? "Yes" : "No"}</td>
                                </tr>
        
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Courses;
