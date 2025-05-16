import React, { useState, useEffect, Fragment } from "react";
import axios from "axios";
import "../styles/EditStudyprogram.css"
import {handleBecomeInCharge, handleBecomeNotInCharge} from "../utils/helpers"
import {fetchAllInstitutes, searchStudyPrograms, fetchStudyPrograms} from "../utils/fetchHelpers"
import { useAuth } from "../components/validateuser";

const EditStudyProgram = () => {
    const [studyPrograms, setStudyPrograms] = useState([]); // Fetched study programs
    const [searchTerm, setSearchTerm] = useState(""); // Current search term

    const [selectedProgram, setSelectedProgram] = useState(null)
    const [editingID, setEditingId] = useState(null)
    const [editingProgram,setEditingProgram] = useState({})
    const [errorMessage,setErrorMessage] = useState("")
    const [errorMessageSearch,setErrorMessageSearch] = useState("")
    const [institutes,setInstitutes] = useState({})
    const [errors,setErrors] = useState({})
    const {currentUser} = useAuth

    // henta fra backend
    useEffect (() => {
        const fetchOnLoad = async () => {
        const inst = await fetchAllInstitutes()
        const progs = await fetchStudyPrograms()
        setInstitutes(inst)
        setStudyPrograms(progs)
        }
      fetchOnLoad();
      }, []);

    // søkebarinput
    const handleSearch = async (e) => {
        const value = e.target.value;
        if(editingID){
            setErrorMessageSearch("Avrbyt eller lagre programmet som blir redigert")
        }else{
        setSearchTerm(value);
        if(value){ // Søke ette program hvis det blir søkt etter noe, ellers fetche alle programmene
            const progs = await searchStudyPrograms(value); 
            setStudyPrograms(progs)
        } else{
            const progs = await fetchStudyPrograms()
            setStudyPrograms(progs)
        }};

    };
    const handleEditClick = (program) => {
        setEditingId(program.id);
        setEditingProgram({ ...program }); // Lagra eksisterende verdier
    };

    const handleCancel = () => {
        setEditingId(null);
        setErrorMessage("")
        setErrorMessageSearch("")
        setEditingProgram({});
        setErrors({})
    };

    const handleSave = (program) => {
        const err = validateForm()
        if (Object.keys(err).length === 0){
            setErrors({})
            try{
        axios.put(`/backend/studyprograms/${editingID}/update`, editingProgram)
            .then(response => {
                                program = editingProgram
                                setEditingId(null)
            })
            .catch(error => {
                console.error("There was an error updating the program!", error);
            });
        }catch(error) {
            console.error("Failed to log in:", error);
        }}else{
            setErrors(err)
        }

    };
    const validateForm = () =>{ 
        const formErrors = {}
        if (!editingProgram.name)
          formErrors.name = "Vennligst skriv noe her"
    
        if (!editingProgram.program_code)
          formErrors.program_code = "Vennligst skriv noe her"
        return formErrors
    }
    

    // Håndtere endringer i input
    const handleFieldChange = (e) => {
        const { name, value } = e.target;
        setEditingProgram((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const toggleMoreInfo = (id) => {
        if(editingID){
            setErrorMessage("Avbryt eller lagre før du lukker fanen")
        }
        else if (selectedProgram === id){
            setSelectedProgram(null)
            setErrorMessage("")
        }else {
            setErrorMessage("")
            setSelectedProgram(id)
        }
    }
    

    

    return (
        <div className="Edit-Study-Program-Page">
            <h1  >Rediger et studieprogram</h1>

            {/* søkebar */}
            <input
                type="text"
                placeholder="Search by Name"
                value={searchTerm}
                onChange={handleSearch}
                style={{ marginBottom: "20px", width: "100%", padding: "10px", fontSize: "16px" }}
            />
            {errorMessageSearch && <div>{errorMessageSearch}</div>}
            {/* studieprogramtabell */}
            <table >
                <thead>
                    <tr className="Program-Table-Title" >
                        <th scope="col" className="th1">Navn</th>
                        <th scope="col" className="th2">Nivå</th>
                        <th scope="col" className="th3">Institutt</th>
                        <th scope="col" className="th4">Handling</th>
                    </tr>
                </thead>
                <tbody style={{ width:"100%" }}>
                    {studyPrograms.map((program) => (
                    <Fragment key={program.id}>
                        <tr  onClick={() => toggleMoreInfo(program.id)} className={`Program-Table-Title${selectedProgram === program.id ? "-Aktiv" :""} `} >
                            
                            <td className="table-content1" >
                                <h4 className="Program-Table-Title-h4">{program.name}</h4>
                            </td>
                            <td className="table-content2">
                                <h4 className="Program-Table-Title-h4">{program.degree_type}</h4>
                            </td>
                            <td className="table-content3">
                                <h4 className="Program-Table-Title-h4">{program.institute.name}</h4>
                            </td>
                            { selectedProgram===program.id ? <td className="table-content4">&#11205;</td> :<td className="table-content4">&#11206;</td>}
                        </tr>
                        {selectedProgram === program.id && 
                        <tr className="Program-Table-Info">

                            {editingID === program.id ? (
                                <td className="expanded" >
                                    <div>
                                        <h4>Navn</h4>
                                        <input onChange={handleFieldChange} name="name" value={editingProgram.name}/>
                                        {errors.name && <h1>{errors.name}</h1>}
                                    </div>
                                    <div>
                                        <h4>Studienivå</h4>
                                        <select onChange={handleFieldChange} value={editingProgram.degree_type} name="degree_type">
                                            <option value="Bachelor" >Bachelor</option>
                                            <option value="Master">Master</option>
                                        </select>
                                    </div>
                                    <div>
                                        <h4 >Institutt</h4>
                                        <select name="institute" value={editingProgram.institute.id} onChange={handleFieldChange}>
                                                {institutes &&institutes.map(inst=> (
                                            <option key={inst.id} value={inst.id}>{inst.name}</option>))}
                                        </select>
                                    </div>
                                    <div >
                                        <h4>Studieprogramkode</h4>
                                        <input onChange={handleFieldChange} value={editingProgram.program_code} name="program_code"/>
                                        {errors.program_code && <h1>{errors.program_code}</h1>}
                                        </div>
                                    <div>
                                        <h4>Antall Semester</h4>
                                        <p>{program.semester_number}</p>
                                    </div>
                                    <div>
                                        <h4>Ansvarlig</h4>
                                        <p>{program.program_ansvarlig ? program.program_ansvarlig_id   :<div> Ingen<button onClick={() => handleEditClick(handleBecomeInCharge(program.id))}>Bli Ansvarlig</button></div>}</p>
                                    </div>
                                    <div>
                                        <h4>Program Aktivt?</h4>
                                        <p>{program.is_active ? "Ja" : "Nei"}</p>
                                    </div>
                                    {errorMessage && errorMessage}
                                    <div>
                                        <button onClick={() => handleSave(program)}>Lagre endringer</button>
                                        <button onClick={() => handleCancel()}>Avbryt</button>
                                        
                                    </div>
                            </td>
                            ) : (
                                <td className="expanded" >
                                    <div>
                                        <h4 className="Program-Table-Info-h4" >Studieprogramkode</h4>
                                        <p>{program.program_code}</p>
                                    </div>
                                    <div>
                                        <h4 className="Program-Table-Info-h4">Antall Semester</h4>
                                        <p>{program.semester_number}</p>
                                    </div>
                                    <div>
                                        <h4 className="Program-Table-Info-h4">Ansvarlig</h4>
                                        <p>{program.program_ansvarlig ? program.program_ansvarlig_id===currentUser &&<div> {program.program_ansvarlig.name} <button onClick={() => handleBecomeNotInCharge(program.id)}>Ikke vær Ansvarlig</button> </div>: "Ingen"}</p>
                                    </div>
                                    <div>
                                        <h4 className="Program-Table-Info-h4">Program Aktivt?</h4>
                                        <p>{program.is_active ? "Ja" : "Nei"}</p>
                                    </div>
                                    <div>
                                        <button onClick={() => handleEditClick(program)}>Rediger Studieprogram</button>
                                    </div>
                                </td>
                            )}
                            

                        </tr>
                        }
                    </Fragment>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default EditStudyProgram;
