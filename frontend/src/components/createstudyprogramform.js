import axios from "axios";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Forms.css";


export default function CreateStudyProgramForm() {
  const navigate = useNavigate();
  const [institutes, setInstitutes] = useState([])

  const [formData, setFormData] = useState({
    "studyprogram_name": "",
    "degree": "",
    "institute": "",
    "semester_number": "",
    "program_code": ""
  })

  const [errors, setErrors] = useState({})

  useEffect(() => {
    const getInstitutes = async () => {
      await axios.get('/backend/institutes/get_all')
        .then(response => {
          setInstitutes(response.data)
        })

        .catch(error => {
          console.log(error)
        })
    }
    getInstitutes();

  }, []);

  const handleFieldChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  }

  const validateForm = (formData) => {
    const formErrors = {}
    if (!formData.degree)
      formErrors.degree = "Velg en av alternativene"

    if (!formData.institute)
      formErrors.institute = "Velg en av alternativene"

    if (!formData.studyprogram_name)
      formErrors.studyprogram_name = "Vennligst skriv inn et navn"

    if (!formData.semester_number)
      formErrors.semester_number = "Vennligst tast inn hvor mange semester studieprogrammet skal ha"

    if (!formData.program_code)
      formErrors.program_code = "Vennligst skriv inn en programkode"
    return formErrors
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const err = validateForm(formData)
    if (Object.keys(err).length === 0) {
      setErrors({})
      try {
        const response = await axios.post("backend/studyprograms/create", formData);
        // window.location.href = `./studyprograms/${response.data.id}`
        const createdProgram = response.data;
        console.log("Program created:", createdProgram);
        navigate("/createSP", { state: { program: createdProgram } });
        // window.location.href = `./createSP`
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
      <h2>Nytt studieprogram</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="studyprogram_name">Studieprogram navn: </label>
          <input name="studyprogram_name" onChange={handleFieldChange}></input>
          {errors.studyprogram_name && <div className="form-error"> {errors.studyprogram_name} </div>}
        </div>
        <div>
          <label htmlFor="degree">Hvilket Nivå </label>
          <select name="degree" onChange={handleFieldChange}>
            <option value="">Velg en</option>
            <option value="Bachelor">Bachelor</option>
            <option value="Master">Master</option>
          </select>
          {errors.degree && <div className="form-error"> {errors.degree} </div>}
        </div>
        <div>
          <label htmlFor="institute">Hvilket institutt er programmet en del av</label>
          <select name="institute" onChange={handleFieldChange}>
            <option value="">Velg en</option>
            {institutes && institutes.map(inst => (
              <option key={inst.id} value={inst.id}>{inst.name}</option>)
            )}
          </select>
          {errors.institute && <div className="form-error"> {errors.institute} </div>}
        </div>
        <div>
          <label htmlFor="semester_number">Antall Semester</label>
          <input name="semester_number" type="number" onChange={handleFieldChange}></input>
          {errors.semester_number && <div className="form-error"> {errors.semester_number} </div>}
        </div>
        <div>
          <label htmlFor="program_code">Studieprogramkode</label>
          <input type="text" name="program_code" onChange={handleFieldChange} ></input>
          {errors.program_code && <div className="form-error"> {errors.program_code} </div>}
          <button type="submit">Send inn</button>
        </div>
      </form>
    </div>
  );
}