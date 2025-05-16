import React, { useState } from "react";
import axios from "axios"
import "../styles/Forms.css";
import { Link } from "react-router-dom";

import { useAuth } from "../components/validateuser";

const Login = () => {
    const [forgottenPassword,setForgottenPassword] = useState(false)
    const {login} =useAuth()
    const [loginInfo, setLoginInfo] = useState({
        email:'',
        password:'',
        forgottenEmail:''
    });
    const [errorMessage, setErrorMessage] = useState('')

    const handleFieldChange = (e) => {
        setLoginInfo({...loginInfo, [e.target.name]: e.target.value});
    }

    const handleLogin = async (e) => {
        e.preventDefault()
        
            const response = await login(loginInfo.email,loginInfo.password)
            if (!response.success) {
                setErrorMessage(response.error)

            }
            else{
            window.location.href='/'}
    }
    const handleForgotten = (e) => {
        if (forgottenPassword){
            setForgottenPassword(false)
            setLoginInfo({
                email:'',
                password:'',
                forgottenEmail:''
            })
        }
        else{
            setErrorMessage('')
            setForgottenPassword(true)
            setLoginInfo({
                email:'',
                password:'',
                forgottenEmail:''
            })
        }

    }
    const handleForgottenSubmit = async (e) => {
        e.preventDefault()
        console.log(loginInfo[2])
        try{
            const response = await axios.post('/backend/user/reset_password', loginInfo);
            alert("Det ble sendt en lenke for å tilbakestille passordet til din e-post")
        } catch(error) {
            console.error("Failed to log in:", error);

        }
    }

    return (
        <div className="form-container" >
            <h2>
                Velkommen til studieplanrevisjon
            </h2>
            {forgottenPassword ? 
            <div className="ForgottenEmail">
                <form onSubmit={handleForgottenSubmit}>
                    <div className="LoginElement">
                        <label htmlFor="forgottenEmail">E-post</label>
                        <input onChange={handleFieldChange} value={loginInfo.forgottenEmail} name="forgottenEmail" type="email" id="forgottenEmail"></input>
                        <button type="submit">Send inn</button>
                        <button onClick={ () => {handleForgotten()}}>Gå tilbake? Trykk her.</button>
                        
                    </div>
                </form>
            </div> : 
            <div className="Login">
            <form onSubmit={handleLogin}>
                <div className="LoginElement">
                    <label htmlFor="email">E-post</label>
                    <input onChange={handleFieldChange} value={loginInfo.email} name="email" type="email" id="email" required></input>
                </div>
                <div className="LoginElement">
                    <label htmlFor="password">Passord</label>
                    <input onChange={handleFieldChange} value={loginInfo.password} name="password" type="password" id="password" required></input>
                </div>
                {errorMessage ? <p className="LoginError">{errorMessage}</p> : null}
                <div className="LoginElement">
                    <button type="submit">Logg inn</button>
                </div>
                
                <div className="LoginElement">
                <button onClick={ () => {handleForgotten()}}>Glemt passord? Trykk her.</button>
                </div>
                <div className="LoginElement">
                    <Link to="/register" >Registrer deg her.</Link>
                </div>
            </form>
            </div>}
            
        </div>
    )
};

export default Login;