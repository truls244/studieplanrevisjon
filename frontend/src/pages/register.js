import React, { useState } from "react";
import { Form, Link } from "react-router-dom";
import axios from "axios"
import { useAuth } from "../components/validateuser";
import "../styles/Forms.css";


const Register = () => {
  const [registerInfo, setRegisterInfo] = useState({
    email: '',
    name: '',
    password1: '',
    password2: ''
  });
  const [errors, setErrors] = useState({})
  const { login } = useAuth()

  const handleFieldChange = (e) => {
    setRegisterInfo({ ...registerInfo, [e.target.name]: e.target.value });
  }

  const validateForm = () => {
    const formErrors = {}
    if (!registerInfo.email) {
      formErrors.mail = "E-postadresse er påkrevd."
    } else if (!/^[^\s@]+@uis\.no$/.test(registerInfo.email)) {
      formErrors.email = 'E-postadressen må være en @uis.no e-postadresse.';
    }

    if (!registerInfo.name.trim()) {
      formErrors.name = "Navn er påkrevd."
    }

    if (!registerInfo.password1) {
      formErrors.password1 = 'Passord er påkrevd';
    } else if (registerInfo.password1.length < 8) {
      formErrors.password1 = 'Passordet må være minst 8 tegn';
    } else if (!/[A-Z]/.test(registerInfo.password1)) {
      formErrors.password1 = 'Passordet må ha minst 1 stor bokstav';
    } else if (!/[a-z]/.test(registerInfo.password1)) {
      formErrors.password1 = 'Passordet må ha minst 1 liten bokstav';
    } else if (!/[0-9]/.test(registerInfo.password1)) {
      formErrors.password1 = 'Passordet må har minst et tall';
    }

    if (!registerInfo.password2) {
      formErrors.password2 = 'Vennligst bekreft passordet';
    } else if (registerInfo.password2 !== registerInfo.password1) {
      formErrors.password2 = 'Passordene er ikke like';
    }
    return formErrors

  }




  const handleRegister = async (e) => {
    e.preventDefault()

    const err = validateForm()
    console.log(err)
    if (Object.keys(err).length === 0) {
      setErrors({})
      try {
        await axios.post('/backend/user/register', registerInfo).then(res => {
          login(registerInfo.email, registerInfo.password1)
          window.location.href = '/verify'
        }).catch(err => {
          console.error(err)
        })

      } catch (error) {
        console.error("Failed to log in:", error);
      }
    }
    else {
      setErrors(err)
    }


  }

  return (
    <div className="form-container">
      <h2>Velkommen til studieplanrevisjon</h2>
      <form onSubmit={handleRegister}>
        <div>
          <label htmlFor="email">E-postadresse</label>
          <input onChange={handleFieldChange} name="email" type="email" id="email" required></input>
          {errors.email ? errors.email : <p> E-postadressen må være en gylig uis.no e-postadresse</p>}
        </div>
        <div>
          <label htmlFor="password">Passord</label>
          <input onChange={handleFieldChange} name="password1" type="password" id="password1" required></input>
          {errors.password ? (
            <p>{errors.password}</p>
          ) : (
            <p>
              Passordet må være minst 8 tegn og må inneholdet minst 1 stor bokstav, liten bokstav og tall.
            </p>
          )}
        </div>
        <div>
          <label htmlFor="password">Gjenta passord</label>
          <input onChange={handleFieldChange} name="password2" type="password" id="password2" required></input>
        </div>

        <div>
          <label htmlFor="email">Navn</label>
          <input onChange={handleFieldChange} name="name" type="text" id="name" required></input>
          {errors.name && errors.name}
        </div>
        <div>
          <button type="submit">Registrer ny bruker</button>
        </div>
      </form>
    </div>
  )
};

export default Register;