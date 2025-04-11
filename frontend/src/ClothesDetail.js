/**
 * ClothesDetail.js - Detailed view for a single clothing item in the OVDR system.
 *
 * @fileoverview Displays item metadata, allows adding to closet, and shows recommendations.
 * Handles multiple effects such as fetching details, recording history, and showing similar items.
 *
 * @author
 * Peini SHE
 */
import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./ClothesDetail.css";


/**
 * ClothesDetail component to view a single clothing item's information, image, and suggestions.
 *
 * @component
 * @param {Object} props
 * @param {string} props.userId - ID of the currently logged-in user.
 * @returns {JSX.Element}
 */
const ClothesDetail = ({ userId }) => {
    const location = useLocation();
    const navigate = useNavigate();
    const { item } = location.state || {};

    const [clothingData, setClothingData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [recommendations, setRecommendations] = useState([]);
    const [message, setMessage] = useState("")
    const [messageType,setMessageType]=useState("");

    /**
     * Fetch detailed clothing information when the component mounts.
     * Validates item existence before sending request.
     */
    useEffect(() => {
        if (!item || !item.id) {
            setError("Invalid item data");
            setLoading(false);
            return;
        }

        // Fetch clothing details from Flask API
        const fetchClothingDetail = async () => {
            try {
                const response = await fetch(`http://localhost:5000/detail/${item.id}`);
                const data = await response.json();

                if (response.ok) {
                    setClothingData(data.item);
                } else {
                    setError(data.error || "Failed to fetch item details");
                }
            } catch (err) {
                setError("Failed to fetch item details");
            } finally {
                setLoading(false);
            }
        };

        fetchClothingDetail();
    }, [item]);

  /**
   * Send request to Flask API to store user viewing history.
   */
    useEffect(() => {
        if (!clothingData || !userId) return;
    
        console.log("Recording history:", { user_id: userId, clothing_id: clothingData.id }); 
    
        const recordHistory = async () => {
            try {
                const response = await fetch("http://localhost:5000/add-history", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: userId, clothing_id: clothingData.id }) 
                });
    
                const result = await response.json();
                console.log("History API Response:", result); 
    
            } catch (error) {
                console.error("Failed to record history:", error);
            }
        };
    
        recordHistory();
    }, [clothingData, userId]);
    
  /**
   * Handle adding item to user's virtual closet.
   * Verifies user and item validity, sends POST request to backend.
   */
    const handleAddToCloset = async () => {
        if (!clothingData || !userId) {
            alert("User not logged in or item missing!");
            return;
        }

        try {
            const response = await fetch("http://localhost:5000/add-to-closet", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_id: userId,  
                    clothing_id: clothingData.id,
                }),
            });

            const result = await response.json();
            if (response.ok) {
                setMessage("Successfully added to Try-On Closet.");
                setMessageType("success");
            } else {
                setMessage(result.error);
                setMessageType("error");
            }

            // Auto clear message after 1.5 seconds
            setTimeout(() => {
                setMessage("");
                setMessageType("");
            }, 2000);
        } catch (error) {
            setMessage("Failed to add item.");
            setMessageType("error")

            // Auto clear message after 1.5 seconds
            setTimeout(() => {
                setMessage("");
                setMessageType("");
            }, 1500);
        }
    };
    
  /**
   * Fetch similar clothing recommendations from the backend.
   */
    useEffect(() => {
        if (!item || !item.id) {
            setError("Invalid item data");
            setLoading(false);
            return;
        }
        const getRecommendationsSimilar = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:5000/recommend/${item.id}`);
                const data = await response.json();
                if (data.error) {
                    setError(data.error);
                    setRecommendations([]);
                } else {
                    setRecommendations(data.recommendations);
                    console.log("rec", data.recommendations)
                    setError("");
                }
            } catch (err) {
                setError("Failed to fetch recommendations");
            }
        };
        getRecommendationsSimilar();
    }, [item]);

    if (!item || !item.id) return <h2>Item not found</h2>;
    if (loading) return <h2>Loading...</h2>;
    if (error) return <h2>{error}</h2>;
    if (!clothingData) return <h2>Item not found</h2>;

    return (
        <div className="tryon-container">
            <header className="tryon-header">
                <h1 className="logo">OVDR <span className="title">Clothes Details</span></h1>
                <button className="back-btn" onClick={() => navigate(-1)}>Return</button>
            </header>

            {/* Main content layout */}
            <div className="clothes-content">
                {/* Left side: Large image */}
                <div className="clothes-image">
                    <img src={clothingData.cloth_path} alt={clothingData.title} />
                </div>

                {/* Right side: Outfit details */}
                <div className="clothes-info">
                    <h2 className="clothes-name">{clothingData.title}</h2>

                    {/* Display tags from caption */}
                    <div className="clothes-tags">
                        {clothingData.labels && clothingData.labels.map((label, index) => (
                            <span key={index} className="tag">{label}</span>
                        ))}
                    </div>

                    {/* Add to closet button */}
                    <button className="add-btn" onClick={handleAddToCloset}> ⭐ Add to My Closet</button>
                    {/* Show success or error message */}
                    {message && (
                        <div className={`message ${messageType}`}>
                            {message}
                        </div>
                    )}

                    {/* similarity recommendation */}
                    <div class="similar-clothes">
                        <h3>You may also like</h3>
                        <div className="similar-list">
                            {recommendations.map((item) => (
                                <div key={item.id} className="similar-item" onClick={() => { 
                                    setLoading(true); 
                                    navigate(`/detail/${item.id}`, { state: { item } })
                                    }}>
                                    <img src={item.url} alt="recommendations" className="similar-img"/>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>          

            {/* Footer */}
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

export default ClothesDetail;
