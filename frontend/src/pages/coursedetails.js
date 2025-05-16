
import axios from "axios";
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import "../styles/CourseDetails.css"
import AddPrerequisites from "../components/addprerequisites"

function CourseDetails() {
    const { id } = useParams();
    const [subject, setSubject] = useState({}) // spesifik emne
    const [editingActive, setEditingActive] = useState(false)
    const [isPreReqVisible, setIsPreReqVisible] = useState(false)
    const [studyPrograms, setStudyPrograms] = useState([])
    const [overlappingCourses, setOverlappingCourses] = useState([])
    const [reallyDeleteCourse, setReallyDeleteCourse] = useState(false)
    const [errorMessage, setErrorMessage] = useState('')

    

    useEffect(() => {
            axios.get("/backend/courses/"+id)
                .then(response => {
                    setSubject(response.data)
                })
                .catch(error => {
                    console.error("There was an error fetching the subject!", error);
                });

            axios.get("/backend/courses/course_usage/" +id)
                .then(response => {
                    setStudyPrograms(response.data)
                    console.log(response.data)
                })
                .catch(error => {
                    console.error("Could not get studyplans!", error);
                });

            axios.get("/backend/courses/overlapping_courses/" +id)
                .then(response => {
                    setOverlappingCourses(response.data)
                })
                .catch(error => {
                    console.error("Could not get overlapping courses!", error);
                });
        
    }, [setSubject])

    function handleEdit() {
        if (editingActive) {
            setEditingActive(false)
        }
        if (!editingActive) {
            setEditingActive(true)
        }

    }

    //endrer verdiene når de blir endret
    const handleFieldChange = (e) => {
        const { name, value } = e.target;
        setSubject((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    //Lagrer endringer som blir gjort
    const handleSave = () => {
        axios.put(`/backend/courses/${subject.id}`, subject)
            .then(response => {
                // oppdatere emnelista
                if (response) {
                    alert("Suksess")
                }
                setEditingActive(false); // Exit edit mode
            })
            .catch(error => {
                console.error("Klarte ikke å endre emnet.", error);
            });
    };


    // Viser/gjemmer emnene når knapp blir trykket
    const handlePrerequisiteVisible = () => {
        if (isPreReqVisible) {
            setIsPreReqVisible(false)
        }
        if (!isPreReqVisible) {
            setIsPreReqVisible(true)
        }
    }

    const handleRemovePreRequisite = (e) => {
        axios.delete(`/backend/prerequisites/remove/${subject.id}/${e.id}`)
            .then(response => {
                window.location.reload();
            })
            .catch(error => {
                console.error("Klarte ikke å slette emnet")
            });
    }

    const handleDeleteCourse = () => {
        if (studyPrograms.length !== 0) {
            setErrorMessage("Kan ikke slette emner som er i bruk")
        }
        else if (!reallyDeleteCourse) {
            setReallyDeleteCourse(true)
        }
        else if (studyPrograms.length === 0 && reallyDeleteCourse) {
            console.log("Emnet er slettet")
            axios.delete(`/backend/courses/${subject.id}`)
            alert(`${subject.name} har nå blitt slettet`)
            window.location.href = '/courses/'
        }

    }

    if (editingActive) {
        return (
            <div className="course-detail-container">
                <h2> <input
                    name="name"
                    value={subject.name}
                    onChange={handleFieldChange} /></h2>
                <ul>
                    <li>Emnekode:</li> <input
                        name="courseCode"
                        type="text"
                        onChange={handleFieldChange}
                        value={subject.courseCode}
                    />
                    <li>Antall Studiepoeng: <input
                        name="credits"
                        onChange={handleFieldChange}
                        value={subject.credits}
                    /></li>
                    <li>Semester (H eller V): <input
                        name="semester"
                        onChange={handleFieldChange}
                        value={subject.semester}
                    /></li>
                    <li>Nivå: <input
                        name="degree"
                        onChange={handleFieldChange}
                        value={subject.degree}
                    /></li>
                    <li className="course-details-list-headline" >Forkunnskaper:</li> {subject.prereqs !== undefined && subject.prereqs.length > 0 ?
                        subject.prereqs.map((element) =>
                            <li>{element.name} <button onClick={() => handleRemovePreRequisite(element)}>Fjern</button> </li>)
                        : "Ingen"}

                    <li className="course-details-list-headline">Blir brukt i:</li> {studyPrograms &&
                        studyPrograms.map((element) =>
                            <li className="prereq-item"> {element.name}</li>
                        )}
                    <li className="course-details-list-headline" >Overlapper med</li>
                    {overlappingCourses &&
                        overlappingCourses.map((element) =>
                            <li className="prereq-item"> {element.name}</li>
                        )}
                </ul>
                <button onClick={handleEdit}>Avbryt</button>
                <button onClick={handleSave}>Lagre</button>
            </div>
        )
    }
    return (
        <div class="course-detail-container">
            <h2>{subject.name}</h2>
            <ul>
                <li>Emnekode: {subject.courseCode}</li>
                <li>Antall Studiepoeng: {subject.credits}</li>
                <li>Semester: {subject.semester === "H" && "Høst"}{subject.semester === "V" && "Vår"}</li>
                <li>Nivå: {subject.degree}</li>
                <li className="course-details-list-headline">Forkunnskaper:</li> {subject.prereqs !== undefined && subject.prereqs.length > 0 ?
                    subject.prereqs.map((element) =>
                        <li className="prereq-item">{element.name}</li>)
                    : <li> Ingen </li>}

                <li className="course-details-list-headline">Blir brukt i:</li> {studyPrograms &&
                    studyPrograms.map((element) =>
                        <li className="prereq-item"> {element.name}</li>
                    )}

                <li className="course-details-list-headline" >Overlapper med</li>
                {overlappingCourses &&
                    overlappingCourses.map((element) =>
                        <li className="prereq-item"> {element.name}</li>
                    )}

            </ul>
            <button onClick={handleEdit}>Rediger Emne</button>
            <button onClick={handleDeleteCourse}>Slett Emne</button>
            {errorMessage ? <div>{errorMessage}</div> : null}
            {reallyDeleteCourse ? <div> <p>Er du sikker på at du vil slette {subject.courseCode}?</p><button onClick={() => handleDeleteCourse()}>Ja</button> <button onClick={() => setReallyDeleteCourse(false)}>Nei</button> </div> : null}
            {isPreReqVisible ? <button onClick={handlePrerequisiteVisible} >Avbryt</button> : <button onClick={handlePrerequisiteVisible} >Legg til forkunnskaper</button>}
            <div className="add-prerequisite-container">
                {isPreReqVisible ? <AddPrerequisites parentSubject={subject} /> : null}
            </div>
        </div>
    )
}
export default CourseDetails