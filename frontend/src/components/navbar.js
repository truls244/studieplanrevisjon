import { Link } from "react-router-dom";
import "../styles/NavBar.css";
import { useAuth } from "./validateuser";

const NavBar = () => {

    const { isAuthenticated, logout, currentUser } = useAuth()


    return (
        <nav className="NavBar">
            {isAuthenticated ? (
                <div className="NavBarLoggedIn" >
                    <div className="NavBarLeft">
                        <Link className="NavBarElement" to="/" >
                            <img src="../uis_logo.jpg" />
                            <h3>Forside</h3>

                        </Link>
                        {currentUser.role === "admin" && <Link to={'/admin'}className="NavBarElement" ><h3>Admin</h3></Link>}
                    </div>
                    
                    <div className="NavBarRightSide" >
                        
                        <div className="NavBarElement" >
                            <button onClick={logout}>Logg ut</button>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="NavBarLoggedOut" >
                    <div className="NavBarElement">
                        <Link to="/login" >
                        <img src="../uis_logo.jpg" />
                            <h3>Logg inn</h3>
                        </Link>
                    </div>
                    <div className="NavBarElement">
                        <Link to="/register" >
                            <h3>Registrer</h3>
                        </Link>
                    </div>
                </div>
            )}


        </nav>
    );
}
export default NavBar;