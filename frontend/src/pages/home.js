import { Link } from "react-router-dom";
import "../styles/Home.css";

const Home = () => {
    return (
        <div className="hp-link-container">
            <Link to="createcourse" className="hp-link-box">
                <p to="createcourse" className="hp-link-title">Lag et nytt emne eller valgemne kategori</p>
                <p className="hp-link-info"></p>
            </Link>
            <Link to="createstudyprogram" className="hp-link-box">
                <p  className="hp-link-title">Lag et nytt studieprogram</p>
                <p className="hp-link-info"></p>
            </Link>
            <Link to="editstudyprogram" className="hp-link-box">
                <p  className="hp-link-title">Rediger et studieprogam</p>
                <p>Rediger informasjon til studieprogram</p>
            </Link>
            <Link to="courses"className="hp-link-box">
                <p  className="hp-link-title">Oversikt over emner</p>
                <p className="hp-link-info">Se og endre infromasjon til emner</p>
            </Link>
            
            {/* <div className="hp-link-box">
                <Link to="createstudyplan" className="hp-link">Lag en ny studieplan</Link>
            </div> */}
            <Link to="studyprogram" className="hp-link-box">
                <p className="hp-link-title">Studieplaner</p>
                <p className="hp-link-info">Se studieplaner til studieprogram</p>
            </Link>
        </div>
    );
};

export default Home;