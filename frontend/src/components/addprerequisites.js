import React, {useState,useEffect} from "react";
import axios from "axios";
import "../styles/CourseDetails.css"


function AddPrerequisites( parentSubject ) {
    const [subjects, setSubjects] = useState([]); // All subjects fetched from the backend
    const [filteredSubjects, setFilteredSubjects] = useState([]); // filtersøk på emne
    const [searchTerm, setSearchTerm] = useState(""); // søkeord
    const [prerequisiteList, setPrerequisiteList] = useState([])

    // Henta emner
    useEffect(() => {
        axios.get("http://127.0.0.1:5000/backend/courses/")
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
        console.log(value)
        // Søk på navn/emnekode
        const filtered = subjects.filter((subject) =>
            subject.name.toLowerCase().includes(value) ||
            subject.courseCode.toLowerCase().includes(value)
        );
        setFilteredSubjects(filtered);
    };

    const handleAddToPreReqList = (e) => {
        if (prerequisiteList.includes(e)){
            return false
        }
        setPrerequisiteList(prev =>{
            return [...prev,e];
        })
    }

    const handleRemovePreRequisite = (e) => {
        setPrerequisiteList(oldSubject => {
            return oldSubject.filter(subject => subject !== e )
        })
    }
    const handleSubmitPreRequisite = () => {
        const parentSubjectId = parentSubject.parentSubject.id
        axios.post(`http://127.0.0.1:5000/backend/prerequisites/add/${parentSubjectId}`, prerequisiteList)
            .then(response => {
                if (response){
                    alert("Emnene ble lagt til")
                    setPrerequisiteList([])
                    window.location.reload()
                }})
                .catch(error => {
                    console.error("Klarte ikke å legge til emnene, prøv igjen.", error);
                });

    }

    

    return(
        <div className="add-prerequisite" >
            <div className="add-prereq-list">
                <input className="add-prerequisite-searchfield"
                    type="text"
                    placeholder="Search by Name or Subject Code"
                    value={searchTerm}
                    onChange={handleSearch}
                    style={{ marginBottom: "20px", width: "100%", padding: "10px", fontSize: "16px" }}
                />
                <table className="add-prerequisite-table" >
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Subject Code</th>
                            <th>Semester</th>
                            <th>Credits</th>
                            <th>Legg til</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredSubjects.map((subject) =>
                        {if(subject.id !== parentSubject.parentSubject.id && !parentSubject.parentSubject.prereqs.includes(subject.name)){
                        return(
                        <tr key={subject.id}>
                        <td>{subject.name}</td>
                        <td>{subject.courseCode}</td>
                        <td>{subject.semester}</td>
                        <td>{subject.credits}</td>
                        <td> <button onClick={() => handleAddToPreReqList(subject)}>Legg til emne</button> </td>
                    </tr>
                        )}}
                    )}
                    </tbody>
                </table>
            </div>
            <table className="added-prerequirements" >
                    <thead>
                        <tr>
                            <th>Emnekode</th>
                            <th>Emnenavn</th>
                        </tr>
                    </thead>
                    <tbody>
                        {prerequisiteList.length ? prerequisiteList.map((subject) => 
                        <tr key={subject.id}>
                            <td>{subject.courseCode}</td>
                            <td>{subject.name}</td>
                            <td> <button onClick={() => handleRemovePreRequisite(subject)}>Fjern</button> </td>
                        </tr>
                        ): null }
                        {prerequisiteList.length ? <button onClick={handleSubmitPreRequisite}>Send inn emner</button> : null }
                    </tbody>
                </table>
        </div>
    );
}
export default AddPrerequisites