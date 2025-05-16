import React, { useState } from "react";
import { useAuth } from "../components/validateuser";
import AdminUserList from "../components/adminuserlist";
import AdminLogPage from "../components/adminlogpage";
import AdminProgramList from "../components/adminprogrampage";
import AdminOverload from "../components/adminoverload";

const Admin = () => {

    const [activePage, setActivePage] = useState('welcome');
    const { currentUser, isAuthenticated } = useAuth()

    return (
        <div>{isAuthenticated ?
            <div>
                <div className="w-64 bg-gray-800 text-white">
                    <div className="p-4">
                        <h1 className="text-2xl font-bold">Admin Panel</h1>
                    </div>
                    <nav className="mt-4">
                        <button
                            className={`flex items-center w-full px-4 py-3 ${activePage === 'users' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
                            onClick={() => setActivePage('userList')}
                        >
                            <span className="ml-2">Brukerliste</span>
                        </button>
                        <button
                            className={`flex items-center w-full px-4 py-3 ${activePage === 'logs' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
                            onClick={() => setActivePage('logs')}>
                            <span className="ml-2">Loggside</span>
                        </button>
                        <button
                            className={`flex items-center w-full px-4 py-3 ${activePage === 'programs' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
                            onClick={() => setActivePage('programs')}>
                            <span className="ml-2">Studieprogramliste</span>
                        </button>
                    </nav>
                </div>
                <div>
                    {activePage === 'welcome' && <div> Velkommen til admininistatorsiden</div>}
                    {activePage === 'userList' && <AdminUserList />}
                    {activePage === 'logs' && <AdminLogPage />}
                    {activePage === 'programs' && <AdminProgramList />}
                    {activePage === 'overloadedprograms' && <AdminOverload />}
                </div>
            </div>
            :
            <div>

            </div>}
        </div>
    )
}

export default Admin