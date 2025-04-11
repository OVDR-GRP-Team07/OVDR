/**
 * FullCloset.js - View and manage all clothing items in the user's virtual closet.
 *
 * @fileoverview Allows searching, filtering by category, and viewing popular recommendations.
 * Integrates with backend APIs for dynamic content updates and user interaction tracking.
 *
 * @author
 * Peini SHE
 */

import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useLocation } from "react-router-dom";
import "./FullCloset.css";

/**
 * FullCloset component renders the full virtual closet interface with category filter, search,
 * user account dropdown, and popular item sidebar.
 *
 * @component
 * @param {Object} props
 * @param {string} props.username - Username for greeting in account dropdown.
 * @param {string} props.userId - ID of the currently logged-in user.
 * @returns {JSX.Element}
 */
const FullCloset = ({ username, userId }) => {
    const navigate = useNavigate();
    const timeoutRef = useRef(null);      
    const storedCategory = sessionStorage.getItem("selectedCategory") || "tops";  // Default category is "tops"
    
    const [category, setCategory] = useState(storedCategory); 
    const [showDropdown, setShowDropdown] = useState(false);
    const [closetImages, setClosetImages] = useState([]);
    const [searchingResult, setSearchingResult] = useState([]);
    const [recommendations, setRecommendations] = useState([]);

    // Retrieve user ID from localStorage if not provided as a prop
    const storedUserId = localStorage.getItem("user_id");
    const effectiveUserId = userId || storedUserId;
    const [error, setError] = useState("");    
    const [searchQuery, setSearchQuery] = useState("");
    const [isSearching, setIsSearching] = useState(false);
       
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const query = queryParams.get("query"); 
  
    useEffect(() => {
        if (query) {
          fetch(`http://localhost:5000/search?query=${query}`)
            .then((res) => res.json())
            .then((data) => setSearchingResult(data.items || []))
            .catch(() => setSearchingResult([]));
          setIsSearching(true);
        }
    }, [query]);

    /**
   * Fetch clothing items from the backend based on selected category.
   */
    useEffect(() => {
        console.log("Checking userId in FullCloset:", effectiveUserId);
    }, [effectiveUserId]);

    useEffect(() => {
        if (!effectiveUserId) {
            console.warn("No userId provided. Unable to fetch closet.");
            return;
        }

        const fetchImages = async () => {
            try {
                const response = await fetch(`http://localhost:5000/api/clothes?category=${category}&user_id=${effectiveUserId}`);
                const data = await response.json();
                if (data.items) {
                    setClosetImages(data.items);
                    console.log("Fetched images:", data.items);
                } else {
                    console.warn("No closet items found.");
                    setClosetImages([]); // Ensure the state is reset when no items are found
                }
            } catch (error) {
                console.error("Error fetching images:", error);
                setClosetImages([]); // Ensure UI remains stable even if the fetch fails
            }
        };
        fetchImages();
    }, [category, effectiveUserId]);

  /**
   * Fetch top 5 most popular clothing recommendations.
   */    
    useEffect(() => {
        const getRecommendationsPopular = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:5000/recommend/popular`);
                const data = await response.json();
                if (data.error) {
                    setError(data.error);
                    setRecommendations([]);
                } else {
                    setRecommendations(data.recommended_popular);
                    setError("");
                }
            } catch (err) {
                setError("Failed to fetch combinations");
            }
        };
        getRecommendationsPopular();
    }, []);

  /**
   * Handles keyword-based search.
   * @param {KeyboardEvent} e - Keyboard event from input.
   */
    const handleSearch = async (e) => {
        if (e.key === "Enter" && searchQuery.trim() !== "") {
            setIsSearching(true);
            try {
                const response = await fetch(`http://127.0.0.1:5000/search?query=${searchQuery}`);
                const data = await response.json();
                console.log("Search API Response:", data.items);
                setSearchingResult(data.items || []);
            } catch (err) {
                console.error("Search error:", err);
                setError("Failed to fetch search results");
                setSearchingResult([]);
            }
        }
    };

    return (
        <div className="tryon-container">
            {/* Header */}
            <header className="tryon-header">
                <h1 className="logo">OVDR <span className="title">All Clothes</span></h1>

                {/* Search Bar */}
                <input 
                    type="text" 
                    className="search-bar" 
                    placeholder="Search by keywords to access the clothes you like" 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleSearch}
                />

                {/* Category Dropdown Selection */}
                <select className="category-dropdown" value={category} onChange={(e) => {
                    const newCategory = e.target.value;
                    setCategory(newCategory);
                    sessionStorage.setItem("selectedCategory", newCategory); // Store selection in session to persist after navigation
                }}>
                    <option value="tops">Tops</option>
                    <option value="dresses">Dresses</option>
                    <option value="bottoms">Bottoms</option>
                </select>

                {/* Account Dropdown */}
                <div className="account-container"
                    onMouseEnter={() => {
                        if (timeoutRef.current) {
                            clearTimeout(timeoutRef.current);
                        }
                        setShowDropdown(true);}}
                    onMouseLeave={() => {timeoutRef.current = setTimeout(() => {
                        setShowDropdown(false);
                    }, 500);}}
                >
                    <button className="account-btn">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2Z"></path>
                            <path d="M12 6a3 3 0 1 1-3 3 3 3 0 0 1 3-3ZM6 18a6 6 0 0 1 12 0"></path>
                        </svg>
                    </button>
                    {showDropdown && (
                        <div className="account-dropdown">
                            <div className="account-info">Hello {username}!</div>
                            <div className="dropdown-item" onClick={() => navigate(`/history?user_id=${userId}`)}>
                                View My History 
                            </div>
                            <div className="dropdown-item" onClick={() => navigate("/login")}>Log out</div>
                        </div>
                    )}
                </div>

                <button className="back-btn" onClick={() => navigate("/tryon")}>
                    Back to dressing room
                </button>
            </header>
            
            {/* Grid Layout for Clothes */}
            <div className="closet-grid">
                {isSearching ? (
                    searchingResult.length > 0 ? (
                        searchingResult.map((item, index) => (
                            <div 
                                className="closet-item" 
                                key={item.id || `search-${index}`}
                                onClick={() => navigate(`/detail/${item.id}`, { state: { item, category, userId: effectiveUserId } })}
                            >
                                <img src={item.image_path} className="closet-img" alt={item.title} />
                                <div className="closet-text">
                                    <h3>{item.title.length > 25 ? item.title.slice(0, 22) + "..." : item.title}</h3>
                                    <p>{item.closet_users} people added this to their Closet</p>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p>No search results found.</p>
                    )
                ) : (
                    closetImages.length > 0 ? (
                        closetImages.map((item, index) => (
                            <div 
                                className="closet-item" 
                                key={item.id || `closet-${index}`} 
                                onClick={() => navigate(`/detail/${item.id}`, { state: { item, category, userId: effectiveUserId } })}
                            >
                                <img 
                                    src={item.image_path} 
                                    className="closet-img" 
                                    alt={item.title}
                                    onError={(e) => {
                                        console.error(`Failed to load image: ${item.image_path}`);
                                        e.target.src = "/images/placeholder.jpg";
                                    }}
                                />
                                <div className="closet-text">
                                    <h3>{item.title.length > 25 ? item.title.slice(0, 22) + "..." : item.title}</h3>
                                    <p>{item.closet_users} people added this to their Closet</p>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p>No items found.</p>  
                    )  
                )}
            </div>

            {/* Popular Clothes Sidebar */}
            <div className="popular-list">
                <h3>Top 5 Popular Items</h3>
                {recommendations.length > 0 ? (
                    recommendations.map((item) => (
                        <div 
                            className="popular-item" 
                            key={item.id} 
                            onClick={() => navigate(`/detail/${item.id}`, { state: { item, category, userId: effectiveUserId } })}
                        >
                            <img 
                                src={item.url} 
                                alt={item.title} 
                                className="popular-img"
                                onError={(e) => {
                                    console.error(`Failed to load image: ${item.image_path}`);
                                    e.target.src = "/images/placeholder.jpg";
                                }}
                            />
                        </div>
                    ))
                ) : (
                    <p>No recommendations found.</p>
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

export default FullCloset;
