import './styles/App.css';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Outlet
} from "react-router-dom";
import React from 'react';
import Home from './pages/home';
import CreateCourse from './pages/createcourse';
import CreateStudyProgram from './pages/createstudyprogram';
import Courses from './pages/courses';
import EditStudyProgram from './pages/editstudyprogram';
import NavBar from './components/navbar';
import StudyProgram from './pages/studyprogram';
import StudyProgramDetail from './pages/studyprogramdetail';
import GenerateStudyplan from './pages/generatestudyplan';
import CourseDetails from './pages/coursedetails';
import Login from './pages/login';
import Register from './pages/register';
import Verify from './pages/verify';
import VerifyToken from './pages/verifytoken';
import ProtectedRoute from './components/protectedroute';
import { AuthProvider } from './components/validateuser';
import { CoursesProvider } from './utils/CoursesContext';
import ResetPassword from './pages/resetpassword';
import axios from 'axios';
import CreateSP from './pages/createsp';
import Admin from './pages/admin'
import { ProgramProvider } from './utils/programContext';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}


function App() {
  axios.interceptors.request.use(config => {
  // Get the CSRF token from cookies
  const csrfToken = getCookie('csrf_access_token');
  if (csrfToken) {
    // Set the header that Flask-JWT-Extended expects
    config.headers['X-CSRF-TOKEN'] = csrfToken;}
    return config;
    },error => {
    return Promise.reject(error);
  });



  axios.defaults.withCredentials = true

  return (
    <Router>
      <AuthProvider>
        <ProgramProvider>
          <CoursesProvider>
            <NavBar />
            <Routes>
              <Route element={<ProtectedRoute />}>
                <Route path="/" element={<Home />} />
                <Route path="/createcourse" element={<CreateCourse />} />
                <Route path="/createstudyprogram" element={<CreateStudyProgram />} />
                <Route path="/courses" element={<Courses />} />
                <Route path='/courses/details/:id' element={<CourseDetails />} />
                <Route path="/editstudyprogram" element={<EditStudyProgram />} />
                <Route path="/studyprogram" element={<StudyProgram />} />
                <Route path="/studyprograms/:id" element={<StudyProgramDetail />} />
                <Route path="/generatestudyplan/:id" element={<GenerateStudyplan />} />
                <Route path="/createsp" element={<CreateSP />} />
                <Route path="/admin" element={<Admin />} />
              </Route>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/verify" element={<Verify />} />
              <Route path="/verifytoken/:token" element={<VerifyToken />} />
              <Route path="/reset_password/:token" element={<ResetPassword />} />
            </Routes>
          </CoursesProvider>
        </ProgramProvider>
      </AuthProvider>
    </Router>

  );
}

export default App;