import React from "react";
import axios from "axios";


export default function CreateCourseForm() {

  function submitCourseForm(formData) {
    const coursecode = formData.get("coursecode")
    const coursename = formData.get("coursename")
    const coursesemester = formData.get("coursesemester")
    const coursecredits = formData.get("coursecredits")
    const data = {
      code: coursecode,
      name: coursename,
      semester: coursesemester,
      credits: coursecredits
    }
    axios.post('http://127.0.0.1:5000/backend/courses/create', data, {"withCredentials" : true})
      .then((response) => console.log(response))
      .catch((error) => console.log(error))
  }

  return (
    <form action={submitCourseForm}>
      <label htmlFor="coursecode">Emnekode: </label>
      <input name="coursecode"></input>
      <label htmlFor="coursename">Emnenavn: </label>
      <input name="coursename"></input>
      <label htmlFor="coursesemester">Velg hvilket semester: </label>
      <select id="coursesemester" name="coursesemester">
        <option value="H">Høst</option>
        <option value="V">Vår</option>
      </select>
      <label htmlFor="coursecredits">Antall studiepoeng emne gir: </label>
      <input name="coursecredits"></input>
      <button type="submit">Send inn</button>
    </form>
  );
}

