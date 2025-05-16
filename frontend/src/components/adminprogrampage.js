import React, { useContext, useEffect, useState} from "react";
import { Link } from "react-router-dom";
import "../styles/NavBar.css";
import axios from "axios"
import { useAuth } from "./validateuser";

const AdminProgramList = () => {
    const [studyPrograms, setStudyPrograms] = useState([]);

    useEffect (() => {
            const getUsers = async () => {
            await axios.get('/backend/studyprograms/getAllStudyPrograms')
            .then(response => {
                setStudyPrograms(response.data)})
            .catch( error => {
                console.log(error)
            })
            }
        getUsers();

    }, []);

    const handleDeleteProgram = (e) => {
        axios.delete("/backend/studyprograms/"+e)
        .then(response => console.log(response))
        .catch(response => console.log(response))
    }
    
    return(
        <div>
            <h2>Liste over studieprogrammene</h2>
            <div>
                <table>
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Navn</th>
                            <th>Ansvarlig</th>

                        </tr>
                    </thead>
                    <tbody>
                        {studyPrograms.map(studyprogram=> (
                            <tr>
                                <td>{studyprogram.id}</td>
                                <td>{studyprogram.name}</td>
                                <td>{studyprogram.program_ansvarlig ? studyprogram.program_ansvarlig.name : "ingen"}</td>
                                <td><button onClick={() => { if (window.confirm(`Er du sikker på at du vil slette ${studyprogram.name}?`)) handleDeleteProgram(studyprogram.id) } } >Slett studieprogram</button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
export default AdminProgramList;