/**
 * Home.js - Landing page for the Online Virtual Dressing Room (OVDR) app.
 *
 * @fileoverview Serves as the welcome screen and provides entry points for login and registration.
 * Includes simple navigation buttons and project description.
 *
 * @author
 * Peini SHE & Zixin Ding (layout)
 */

import React from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";

/**
 * Home component provides the main landing page with navigation to login/register.
 *
 * @component
 * @returns {JSX.Element}
 */
function Home() {
    const navigate = useNavigate();

    return (
        <div className="home-wrapper">
            <div className="home-container">
                <h1 className="hero-title">Welcome to Online Virtual Dressing Room! </h1>
                <h3 className="hero-subtitle">with Advanced Try-On and Clothing Retrieval Features</h3>
                <input
                    className="loginButton"
                    type="button"
                    onClick={() => navigate('/login')}
                    value="Log in"
                />
            </div>

            <footer className="footer">
                <p>[P2024-16] Online Virtual Dressing Room with Advanced Try-On and Clothing Retrieval Features</p>
                <p>GRP.TEAM2024.07</p>
            </footer>
        </div>
    );
}

export default Home;
