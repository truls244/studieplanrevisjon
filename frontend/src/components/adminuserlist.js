import React, { useContext, useEffect, useState} from "react";
import { Link } from "react-router-dom";
import "../styles/NavBar.css";
import axios from "axios"
import { useAuth } from "./validateuser";

const AdminUserList = () => {
    const [users, setUsers] = useState([]);
    const [message, setMessage] = useState("")

    useEffect (() => {
            const getUsers = async () => {
            await axios.get('/backend/user/get_all_users')
            .then(response => {
                setUsers(response.data)})
            .catch( error => {
                console.log(error)
            })
            }
        getUsers();

    }, []);

    const handleDeleteUser = (e) => {
        e.preventDefault()
        axios.delete("/backend/user/delete/"+e.id)
        .then(setMessage(`Brukeren ${e.email} ble slettet`))
        .catch(setMessage(`Klarte ikke å slette ${e.email}`))
    }
    
    return(
        <div>
            <h2>Liste over brukere</h2>
            {message && message}
            <div>
                <table>
                    <thead>
                        <tr>
                            <th>Id</th>
                            <th>Navn</th>
                            <th>Epostadresse</th>
                            <th>Rolle</th>
                            <th>Verifisert</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(user=> (
                            <tr>
                                <td>{user.id}</td>
                                <td>{user.name}</td>
                                <td>{user.email}</td>
                                <td>{user.role}</td>
                                <td>{user.verified ? "Ja" : "Nei"}</td>
                                {user.role !== "admin" &&  <td><button onClick={() => handleDeleteUser(user)} >Delete</button></td>}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
export default AdminUserList;