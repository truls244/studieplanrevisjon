import React, { useState, useEffect } from "react";
import axios from "axios";

const EditCourse = () => {
    const [subjects, setSubjects] = useState([]); // All subjects fetched from the backend
    const [filteredSubjects, setFilteredSubjects] = useState([]); // filtersøk på emne
    const [searchTerm, setSearchTerm] = useState(""); // søkeord
    const [editingSubjectId, setEditingSubjectId] = useState(null); // endre basert på ID
    const [editedSubject, setEditedSubject] = useState({}); // Etter emne er endret.

    // Henta emner
    useEffect(() => {
        axios.get("http://127.0.0.1:5000/backend/subjects/")
            .then(response => {
                setSubjects(response.data);
                setFilteredSubjects(response.data); 
            })
            .catch(error => {
                console.error("There was an error fetching the subjects!", error);
            });
    }, []);

    // søkebar input
    const handleSearch = (e) => {
        const value = e.target.value.toLowerCase();
        setSearchTerm(value);

        // Søk på navn/emnekode
        const filtered = subjects.filter((subject) =>
            subject.name.toLowerCase().includes(value) ||
            subject.subjectCode.toLowerCase().includes(value)
        );
        setFilteredSubjects(filtered);
    };

    // Klikk på navnet for å redigera
    const handleEditClick = (subject) => {
        setEditingSubjectId(subject.id);
        setEditedSubject({ ...subject }); // Lagra eksisterende verdier
    };

    // Håndtere endringer i input
    const handleFieldChange = (e) => {
        const { name, value } = e.target;
        setEditedSubject((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    // Lagre endringer i databasen
    const handleSave = () => {
        axios.put(`http://127.0.0.1:5000/backend/subjects/${editingSubjectId}`, editedSubject)
            .then(response => {
                // oppdatere emnelista
                setSubjects((prevSubjects) =>
                    prevSubjects.map((subject) =>
                        subject.id === editingSubjectId ? response.data : subject
                    )
                );
                setFilteredSubjects((prevFiltered) =>
                    prevFiltered.map((subject) =>
                        subject.id === editingSubjectId ? response.data : subject
                    )
                );
                setEditingSubjectId(null); // Exit edit mode
            })
            .catch(error => {
                console.error("There was an error updating the subject!", error);
            });
    };

    // Avbryte redigering
    const handleCancel = () => {
        setEditingSubjectId(null);
        setEditedSubject({});
    };

    return (
        <div>
            <h1>Edit Subjects</h1>

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
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {filteredSubjects.map((subject) =>
                        editingSubjectId === subject.id ? (
                            <tr key={subject.id}>
                                <td>
                                    <input
                                        type="text"
                                        name="name"
                                        value={editedSubject.name}
                                        onChange={handleFieldChange}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="text"
                                        name="subjectCode"
                                        value={editedSubject.subjectCode}
                                        onChange={handleFieldChange}
                                    />
                                </td>
                                <td>
                                    <select
                                        name="semester"
                                        value={editedSubject.semester}
                                        onChange={handleFieldChange}
                                    >
                                        <option value="Høst">Høst</option>
                                        <option value="Vår">Vår</option>
                                    </select>
                                </td>
                                <td>
                                    <input
                                        type="number"
                                        name="credits"
                                        value={editedSubject.credits}
                                        onChange={handleFieldChange}
                                    />
                                </td>
                                <td>
                                    <select
                                        name="is_active"
                                        value={editedSubject.is_active ? "Yes" : "No"}
                                        onChange={(e) =>
                                            setEditedSubject((prev) => ({
                                                ...prev,
                                                is_active: e.target.value === "Yes",
                                            }))
                                        }
                                    >
                                        <option value="Yes">Yes</option>
                                        <option value="No">No</option>
                                    </select>
                                </td>
                                <td>
                                    <button onClick={handleSave}>Save</button>
                                    <button onClick={handleCancel}>Cancel</button>
                                </td>
                            </tr>
                        ) : (
                            <tr key={subject.id}>
                                <td>
                                    <span
                                        style={{ color: "blue", cursor: "pointer", textDecoration: "underline" }}
                                        onClick={() => handleEditClick(subject)}
                                    >
                                        {subject.name}
                                    </span>
                                </td>
                                <td>{subject.subjectCode}</td>
                                <td>{subject.semester}</td>
                                <td>{subject.credits}</td>
                                <td>{subject.is_active ? "Yes" : "No"}</td>
                                <td>
                                    <button onClick={() => handleEditClick(subject)}>Edit</button>
                                </td>
                            </tr>
                        )
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default EditCourse;
