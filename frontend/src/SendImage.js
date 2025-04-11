/**
 * SendImage.js - Component to preview and send try-on result via email.
 *
 * @fileoverview Displays the final result image and provides a form for users to email it to themselves.
 * Validates email input, handles backend API interaction, and displays feedback messages.
 *
 * @author
 * Peini SHE & Zixin DING
 */

import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import './SendImage.css';

/**
 * Utility: Convert image URL to base64 string using FileReader and fetch API
 * @param {string} imageUrl
 * @returns {Promise<string>} base64-encoded image string
 */
const fetchImageAsBase64 = async (imageUrl) => {
    const response = await fetch(imageUrl);
    const blob = await response.blob();

    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
};

/**
 * SaveImage component allows users to view the try-on result and send it to their email.
 *
 * @component
 * @param {Object} props
 * @param {string|null} props.resultImage - URL of the final try-on image.
 * @returns {JSX.Element}
 */
function SaveImage({ resultImage }) {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [message, setMessage] = useState("");

    /**
     * Send the result image to the provided email address.
     * Validates input and calls Flask backend API.
     */
    const sendEmail = async () => {
        if (!email) {
            setMessage("Please enter an email.");
            return;
        }

        try {
            const imageBase64 = await fetchImageAsBase64(resultImage);

            const response = await fetch("http://localhost:5000/send-email", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, imageBase64 }),
            });

            const data = await response.json();
            if (data.success) {
                setMessage("Email sent successfully!");
                setTimeout(() => setMessage(""), 3000);
            } else {
                setMessage("Failed to send email.");
                setTimeout(() => setMessage(""), 3000);
            }
        } catch (error) {
            setMessage("Error sending email.");
            console.error(error);
            setTimeout(() => setMessage(""), 3000);
        }
    };

    return (
        <div className="tryon-container">
            <header className="tryon-header">
                <h1 className="logo">OVDR <span className="title">Save Image</span></h1>
                <button className="back-btn" onClick={() => navigate("/tryon")}>Back to dressing room</button>
            </header>

            <div className="image-preview">
                {resultImage ? (
                    <img src={resultImage} alt="Try-On Result" className="tryon-result" />
                ) : (
                    <p>No image available</p>
                )}
            </div>

            <div className="download-section">
            {message && (
                <div className={`toast ${message.includes("successfully") ? "success" : "error"}`}>
                 {message}
                </div>
            )}
                <input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                    <button onClick={sendEmail} className='send-btn'>Send Image</button>
            </div>


            <footer className="tryon-footer">
            <a href="http://cslinux.nottingham.edu.cn/~Team202407/">About Us</a>
                <a href="/privacy.html" target="_blank" rel="noopener noreferrer">Privacy Policy</a>
                <a href="/docs/user_manual.pdf" target="_blank" rel="noopener noreferrer">Manual</a>
                <a href="/contact.html">Help and Contact</a>
                <p>Developed by TEAM2024.07</p>
            </footer>
        </div>
    );
}

export default SaveImage;