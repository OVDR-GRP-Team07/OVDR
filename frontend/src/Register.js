/**
 * Register.js - User registration page for Online Virtual Dressing Room (OVDR).
 *
 * @fileoverview Handles new user signup, form validation, and backend communication.
 * Redirects to login page upon successful registration.
 *
 * @author
 * Zixin DING
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

/**
 * Register component allows users to sign up for an account.
 *
 * @component
 * @returns {JSX.Element}
 */
function Register() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [passwordConfirm, setPasswordConfirm] = useState("");
    const [message, setMessage] = useState("");
    const [showPopup, setShowPopup] = useState(false);
    const navigate = useNavigate();

  /**
   * Handle registration submission with field validation.
   * If success, redirect to login page after brief delay.
   *
   * @param {React.FormEvent} e - Form submission event
   */
    const handleRegister = async (e) => {
        e.preventDefault(); 

        if (password !== passwordConfirm) {
            setMessage("Passwords do not match.");
            setShowPopup(true);
            return;
        }

        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);
        formData.append("password_confirm", passwordConfirm);

        try {
            const response = await fetch("http://127.0.0.1:5000/register", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                setMessage("Registration successful! Redirecting to login...");
                setShowPopup(true);
                setTimeout(() => navigate("/login"), 2000);
            } else {
                setMessage(data.error);
                setShowPopup(true);
            }
        } catch (error) {
            console.error("Registration failed:", error);
            setMessage(`Error: ${error.message || "Unable to register. Please try again."}`);
            setShowPopup(true);
        }
    };

    return (
        <div className="login-container">
            {showPopup && (
                <div className="popup">
                    <div className="popup-content">
                        <p>{message}</p>
                    </div>
                </div>
            )}
            <h1 className="login">Register</h1>
            <form className="form-wrapper" onSubmit={handleRegister}>
                <input
                    className="textbox"
                    type="text"
                    placeholder="Username length must be 3 to 20 characters"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    className="textbox"
                    type="password"
                    placeholder="Password length must be 6 to 20 characters"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <input
                    className="textbox"
                    type="password"
                    placeholder="Confirm Password"
                    value={passwordConfirm}
                    onChange={(e) => setPasswordConfirm(e.target.value)}
                    required
                />
                <button type="submit" className="login-button">Register</button>
            </form>
            <p className="register-option">
                Already have an account? <a href="/login">Login</a>
            </p>
        </div>
    );
}

export default Register;