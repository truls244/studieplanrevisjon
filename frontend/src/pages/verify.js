import React, { useState } from "react";
import { Form, Link } from "react-router-dom";
import axios from "axios"
import { useAuth } from "../components/validateuser";

const Verify = () => {
    const [result,setResult] = useState('')
    const {currentUser} = useAuth()
    const sendNewLink = () => {
        console.log(currentUser)
        axios.post("backend/user/verify/newtoken",currentUser)
        .then(response => {
            setResult(response.data.message)
        })
        .catch(error => {
            setResult(error.message)
        })
    }
 
    return (
        <div>
            <p>En verifikasjonslink har blitt sendt til din e-mail. Linken utgår etter 1 time fra når du registrerte deg. Se i Søppenpost/Spam-mappen om du ikke finner den.</p>
            {result ? <p>{result}</p>:null}
            <button onClick={() => sendNewLink()} >Send verifikasjonslinken på nytt.</button>
        </div>
    )
};

export default Verify;