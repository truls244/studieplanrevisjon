import React, { useState } from "react";
import { Form, useParams  } from "react-router-dom";
import axios from "axios"



const ResetPassword = () => {
    const {token} = useParams()

    const [formInfo,setFormInfo] = useState({"Pass1": "", "Pass2":""})

    const handleFieldChange = (e) => {
        setFormInfo({...formInfo, [e.target.name]: e.target.value});
    }

    const handleSubmit = async (e)  => {
        e.preventDefault()
        await axios.post(`/backend/user/reset/${token}`, formInfo)
            .then(response => {
                window.location.href='/login'
            })
            .catch(error => {
                console.error("error reseting", error);
                
            });}
    return (
        <div>
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="password">Nytt passord</label>
                    <input onChange={handleFieldChange} name="password1" type="password" id="password1" required></input>
                </div>
                <div>
                    <label htmlFor="password">Gjenta passordet</label>
                    <input onChange={handleFieldChange} name="password2" type="password" id="password2" required></input>
                </div>
                <button type="submit"></button>
            </form>
        </div>
    )
};

export default ResetPassword;