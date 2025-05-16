import React, { useContext, useEffect, useState} from "react";
import { Link } from "react-router-dom";
import "../styles/NavBar.css";
import axios from "axios"
import { useAuth } from "./validateuser";

const AdminOverload = () => {
    const [studyPrograms, setStudyPrograms] = useState([]);

    useEffect (() => {
            const getUsers = async () => {
            await axios.get('/backend/studyprograms/get_plans_with_too_many_credits')
            .then(response => {
                setStudyPrograms(response.data)})
            .catch( error => {
                console.log(error)
            })
            }
        getUsers();

    }, []);
    
    return(
        <div>
            <h3>Liste over studieprogrammene med semester med over 30 poeng i den siste studieplanen</h3>
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
                                <td> {studyprogram.id} </td>
                                <td> <Link to={`/studyprograms/${studyprogram.id}`} >{studyprogram.name}</Link>  </td>
                                <td>{studyprogram.program_ansvarlig ? studyprogram.program_ansvarlig : "ingen"}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
export default AdminOverload;