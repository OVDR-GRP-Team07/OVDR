/**
 * Login.js - User login page for Online Virtual Dressing Room (OVDR).
 *
 * @fileoverview Handles user authentication, input validation, and session state updates.
 * On successful login, stores user info in localStorage and redirects to try-on room.
 *
 * @author
 * Peini SHE
 */

import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import "./Login.css";

/**
 * Login component provides username/password login and feedback messaging.
 *
 * @component
 * @param {Object} props
 * @param {Function} props.setUserId - Setter to store user ID globally.
 * @param {Function} props.setUsername - Setter to store username globally.
 * @returns {JSX.Element}
 */
function Login({ setUserId, setUsername }) {
    const [username, setUsernameLocal] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const [showPopup, setShowPopup] = useState(false);
    const passwordInputRef = useRef(null);
    const navigate = useNavigate();

  /**
   * Handle form submission and login process.
   * Validates input, sends request to backend, updates session state.
   *
   * @param {React.FormEvent} e - Form event
   */
    const handleLogin = async (e) => {
        e.preventDefault(); 

        if (!username || !password) {
            setMessage("Please enter both username and password.");
            setShowPopup(true);
            return;
        }

        // Prepare form data for sending
        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);

        try {
            const response = await fetch("http://127.0.0.1:5000/login", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                const { user_id, username } = data;  // Backend returns user_id
                setUserId(user_id);
                setUsername(username);
                console.log(user_id, username)

                // Store user data globally
                localStorage.setItem("user_id", user_id);  // Ensure that the other components are `user_id`
                localStorage.setItem("username", username);

                setMessage(`Login successful! Welcome, ${username}!`);
                setShowPopup(true);
                setTimeout(() => navigate("/tryon"), 2000);
            } else {
                setMessage("Incorrect username or password.");
                setShowPopup(true);
            }
        } catch (error) {
            setMessage(error.response?.data?.error || "Login failed. Please try again.");
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
            <h1 className="login">Login</h1>
            <input
                className='textbox'
                type="text" 
                placeholder="Username" 
                value={username}
                onChange={(e) => {
                    console.log("Username updated:", e.target.value);
                    setUsernameLocal(e.target.value); 
                }}
                onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        passwordInputRef.current?.focus();
                    }
                }}
            />
            <input
                className='textbox'
                type="password" 
                placeholder="Password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                ref={passwordInputRef}
                onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                        handleLogin(e);
                    }
                }}
            />
            <input
                className='back-to-home'
                type="button"
                onClick={() => navigate("/")}
                value="Back to Home Page"
            />
            <button onClick={handleLogin} className="login-button">
                Continue
            </button>
            <p>Don't have an account yet? <a href="/register">Create an account</a></p>
        </div>
    );
}

export default Login;
