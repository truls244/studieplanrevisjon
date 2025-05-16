import React, { useState } from "react";
import CreateCourseForm from "../components/createcourseform";
import ValgemneKategoriForm from "../components/valgemnekategoriform";
import "../styles/Forms.css";

const CreateCourse = () => {
    const [showCreateCourseForm, setShowCreateCourseForm] = useState(false);
    return (
        <div className="form-container">
            <h1>
                {showCreateCourseForm ? "Valgemne kategorier" : "Create Course"}
            </h1>
            <div>
                {showCreateCourseForm ? (
                    <ValgemneKategoriForm />
                ) : (
                    <CreateCourseForm />
                )}
            </div>
            <button onClick={() => setShowCreateCourseForm(!showCreateCourseForm)}>
                {showCreateCourseForm ? "Bytt til emne" : "Bytt til valgemne kategori"}
            </button>
        </div>
    );
};

export default CreateCourse;