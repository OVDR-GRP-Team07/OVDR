/**
 * History.js - Display user's clothing browsing and try-on history.
 *
 * @fileoverview Fetches and displays historical clothing interactions for the logged-in user.
 * Uses the query string, props, or localStorage to determine user identity.
 *
 * @author
 * Peini SHE
 */

import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import "./History.css";

/**
 * History component displays the logged-in user's history of clothing interactions.
 *
 * @component
 * @param {Object} props
 * @param {string} props.username - Current username.
 * @param {string} props.userId - User ID from props (optional, fallback to URL or localStorage).
 * @returns {JSX.Element}
 */
function History({ username, userId }) {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams(); 
    const urlUserId = searchParams.get("user_id");
    const storedUserId = localStorage.getItem("user_id");
    const effectiveUserId = userId || urlUserId || storedUserId;
    const [historyData, setHistoryData] = useState([]);

  /**
   * Fetch the user's browsing history from backend API.
   */
    useEffect(() => {
        if (!effectiveUserId || effectiveUserId === "null") {
            console.warn("Invalid userId detected:", effectiveUserId);
            setHistoryData([]);
            return;
        }

        const fetchHistory = async () => {
            try {
                const response = await fetch(`http://localhost:5000/get-history?user_id=${effectiveUserId}`);
                const data = await response.json();
                
                if (response.ok && data.history) {
                    console.log("Debug | History Data:", data.history);
                    setHistoryData(data.history);
                } else {
                    console.error("Failed to fetch history:", data.error || "No history available");
                    setHistoryData([]);  
                }
            } catch (error) {
                console.error("Error fetching history:", error);
                setHistoryData([]); 
            }
        };

        fetchHistory();
    }, [effectiveUserId]); 

    return (
        <div className="tryon-container">
            <header className="tryon-header">
                <h1 className="logo">OVDR <span className="title">{username || "Guest"}'s Browsing History</span></h1>
                <button className="back-btn" onClick={() => navigate(-1)}>Return</button>
            </header>

            <div className="history-grid">
                {Array.isArray(historyData) && historyData.length > 0 ? (
                    historyData.map((item, index) => (
                        <div 
                            className="history-item" 
                            key={item.clothing_id || `history-${index}`} 
                            onClick={() => navigate(`/detail/${item.clothing_id}`, { state: { item } })}
                        >
                            <img 
                                src={item.image} 
                                alt={item.title} 
                                className="closet-img" 
                                onError={(e) => {
                                    console.error(`Failed to load image: ${item.image}`);
                                    e.target.src = "/images/placeholder.jpg";
                                }}
                            />
                            <div className="history-text">
                                <h3>{item.title.length > 25 ? item.title.slice(0, 22) + "..." : item.title}</h3>
                                <p>{item.closet_users} people added this to their Closet</p>
                            </div>
                        </div>
                    ))
                ) : (
                    <h2>No history found.</h2>
                )}
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
};

export default History;
