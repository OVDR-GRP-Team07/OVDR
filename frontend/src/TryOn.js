/**
 * TryOn.js - Virtual dressing room component for mixing and matching clothing.
 *
 * @fileoverview Provides try-on functionality, including uploading personal images,
 * generating AI-assisted outfit previews, managing virtual closets, saving combinations,
 * viewing recommendations, and navigating the user interface.
 *
 * @authors
 * - Peini SHE: Initial implementation and layout, reccomendation and result image presentation 
 * - Zhihao CAO: Image generation workflow, result image rendering, combination save and show
 * - Zixin DING:
 *    - Implemented clothing closet panel (category filtering, removal)
 *    - Implemented combination panel (delete combination, display result image on click)
 *    - Implemented search bar interaction (enter-to-search routing)
 *
 * @description
 * This component is the core UI for the virtual try-on experience. It integrates frontend interaction
 * with the backend API for image processing (StableVITON), clothing management, and personalization.
 */

import { useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import "./TryOn.css";

/**
 * TryOn component allows users to preview clothing on their own image, manage closet, and save looks.
 *
 * @component
 * @param {Object} props
 * @param {string} props.username - Current username.
 * @param {string} props.userId - ID of the logged-in user.
 * @param {string|null} props.uploadedImage - User's uploaded image for try-on.
 * @param {Function} props.setUploadedImage - Setter for uploaded image.
 * @param {string|null} props.resultImage - Resulting AI-generated image.
 * @param {Function} props.setResultImage - Setter for generated result image.
 * @returns {JSX.Element}
 */
function TryOn({ username, userId, uploadedImage, setUploadedImage, resultImage, setResultImage }) {
    const navigate = useNavigate();
    const timeoutRef = useRef(null);
    const [showDropdown, setShowDropdown] = useState(false);
    
    const [myCloset, setMyCloset] = useState([]);
    const [combinations, setCombinations] = useState([]);
    const [recommendations, setRecommendations] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState("tops"); 
    const [searchQuery, setSearchQuery] = useState("");
    const [error, setError] = useState("");

    const [activePanel, setActivePanel] = useState(null);

    const handleSearch = (e) => {
        if (e.key === "Enter" && searchQuery.trim() !== "") {
          navigate(`/fullcloset?user_id=${userId}&query=${encodeURIComponent(searchQuery)}`);
        }
    };

    /**
   * Toggle visibility of side panels like closet, combinations, and recommendations.
   * @param {string} panelName - The name of the panel to toggle.
   */
    const togglePanel = (panelName) => {
        setActivePanel((prevPanel) => (prevPanel === panelName ? null : panelName));
    };

    // modified by Zixin Ding: Fix url problem
    // added by Zhihao Cao --->process image and represent the result
    // auto upload without any aother operation---> useEffect
    // tips: the default value of isGenerating is false
    const [isGenerating, setIsGenerating] = useState(false); //generate button must be disabled when generating


 /**
   * Send clothing and user image to backend for generating a virtual try-on preview.
   * @param {string} itemUrl - URL of the selected clothing image.
   * @param {string} itemCategory - Category of clothing (e.g., tops, dresses).
   */

    const handleGenerateImage = async (itemId,itemUrl,itemCategory) => { //itemUrl is the url of the item in the closet
        
        setIsGenerating(true); // disable the button
        if (!uploadedImage) {
            console.error("failed to get user_image");
            window.alert("Please upload your image first"); // alert notification
            return;
        }
        // use document notice to replace the windows.alert() [need user to respond]
        const loadingMessage = document.createElement('div');
        loadingMessage.textContent = "Please wait while the image is being generated...";
        loadingMessage.style.position = 'fixed';
        loadingMessage.style.top = '50%';
        loadingMessage.style.left = '50%';
        loadingMessage.style.transform = 'translate(-50%, -50%)';
        loadingMessage.style.padding = '10px';
        loadingMessage.style.backgroundColor = '#000';
        loadingMessage.style.color = '#fff';
        loadingMessage.style.zIndex = '9999'; // ensure the message is on top of other elements
        document.body.appendChild(loadingMessage);
        try {
            const response = await fetch("http://localhost:5000/process_image", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                mode: "cors",
                // TODO: wait for the user_id to be added
                body: JSON.stringify({
                    item_id: itemId,
                    cloth_url: itemUrl, 
                    user_id: userId,
                    item_category:itemCategory
                }),
            });
            document.body.removeChild(loadingMessage);
            // After consideration: there is no waiting ui for the user to pick the clothes
            const result = await response.json();

            if(!response.ok) {
                
                window.alert("failed to generate"); // alert 
                return;
            } 
            
            // TODO: change resultImage into stable-viton result
            //tips: use "`" to represent the result instead of '' or " "
            const uploadedImager = `/show_image/${userId}/${result.image_path}`;
            setResultImage(uploadedImager);
    
        } catch (error) {
            document.body.removeChild(loadingMessage);
            window.alert(error.message);
        } finally {
            setIsGenerating(false); // re-enable the button
        }
    };

  /**
   * Auto-fetch user's uploaded image from backend if not set.
   */
    useEffect(() => {
        const fetchUserImage = async () => {
            if (!userId || uploadedImage) return;
    
            try {
                const response = await fetch(`http://localhost:5000/get_user_info?user_id=${userId}`);
                const data = await response.json();
                if (response.ok && data.image_path) {
                    const fixedPath = data.image_path.replace(/\\/g, "/");  // Windows fix
                    const fullUrl = `http://localhost:5000/${fixedPath}`;
                    setUploadedImage(fullUrl);
                }
            } catch (error) {
                console.error("Failed to fetch user image", error);
            }
        };
    
        fetchUserImage();
    }, [userId, uploadedImage]);
    

  /**
   * Fetch closet items by selected category.
   */
// Added by Zixin Ding
    useEffect(() => {
        if (!userId) {
            console.warn("No userId provided. Unable to fetch closet.");
            return;
        }

        const fetchCloset = async () => {
            try {
                const response = await fetch(`http://localhost:5000/get-closet?user_id=${userId}&category=${selectedCategory}`);
                const data = await response.json();

                if (data.error) {
                    setError(data.error);
                    setMyCloset([]);
                } else {
                    setMyCloset(data.closet);
                    setError("");
                }
            } catch (err) {
                setError("Failed to fetch closet items");
            }
        };

        fetchCloset();
    }, [selectedCategory, userId]);  // Monitor category change


  /**
   * Remove a clothing item from the user's closet.
   * @param {string} clothingId - ID of the clothing to remove.
   */
    // Added by Zixin Ding
    const handleRemoveFromCloset = async (clothingId) => {
        try {
            const response = await fetch("http://localhost:5000/remove-from-closet", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId, clothing_id: clothingId }),
            });

            const result = await response.json();
            if (response.ok) {
                setMyCloset(myCloset.filter(item => item.id !== clothingId));  
            } else {
                setError(result.error);
            }
        } catch (error) {
            setError("Failed to remove item.");
        }
    };

  /**
   * Save a clothing combination with optional result image.
   */
    const handleSaveCombination = async () => {
        // if (!resultImage) {
        //     console.error("No outfit image available");
        //     return;
        // }
        // authored by Zhihao Cao
        const selectedTop = myCloset.find(item => item.category === "tops")?.id || null;
        const selectedBottom = myCloset.find(item => item.category === "bottoms")?.id || null;
        const selectedDress = myCloset.find(item => item.category === "dresses")?.id || null;
        if (!resultImage) {
            window.alert("please try on firstly")
            return;
        }
        const response = await fetch("http://127.0.0.1:5000/save-combination", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: userId,
                top_id: selectedTop,
                bottom_id: selectedBottom,
                dress_id: selectedDress,
                // TODO: fix to true result
                resultImage: resultImage
            })
        });
        const data = await response.json();
        if (!response.ok) {
            window.alert("save failed")
            return;
        }
        console.log("Saved outfit:", data);

        if (response.ok) {
            setCombinations(prev => [...prev, { id: data.id, image: data.url }]);
            window.alert(data.message); 
            if (data.message === "Combination saved!") {
                setCombinations(prev => [...prev, { id: data.id, image: data.url }]);
            }
        }
    }

  /**
   * Load previously saved clothing combinations.
   */
    useEffect(() => {
        if (!userId) {
            console.warn("No userId provided. Unable to fetch combinations.");
            return;
        }

        const getCombinations = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:5000/get-combinations?user_id=${userId}`);
                const data = await response.json();
                if (data.error) {
                    setError(data.error);
                    setCombinations([]);
                } else {
                    setCombinations(data.combinations);
                    setError("");
                }
            } catch (err) {
                setError("Failed to fetch combinations");
            }
        };
        getCombinations();
    }, [userId]); 

  /**
   * Fetch personalized clothing recommendations.
   */
    useEffect(() => {
        if (!userId) {
            console.warn("No userId provided. Unable to fetch recommendations.");
            return;
        }

        const getRecommendationsPersonal = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:5000/recommend/user/${userId}`);
                const data = await response.json();
                if (data.error) {
                    setError(data.error);
                    setRecommendations([]);
                } else {
                    setRecommendations(data.personalized_recommendations);
                    setError("");
                }
            } catch (err) {
                setError("Failed to fetch recommendations");
            }
        };
        getRecommendationsPersonal();
    }, [userId]);

    const handleDeleteCombination = async (combinationId) => {
        try {
            const response = await fetch("http://localhost:5000/delete-combination", {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: combinationId }),
            });
    
            const result = await response.json();
            if (response.ok) {
                setCombinations(prev => prev.filter(c => c.id !== combinationId));
                // window.alert("Deleted successfully!");
            } else {
                setError(result.error || "Failed to delete combination");
            }
        } catch (error) {
            setError("Request failed: " + error.message);
        }
    };
    


    return (
        <div className="tryon-container">
            {/* Header */}
            <header className="tryon-header">
                <h1 className="logo">OVDR</h1>
                <input 
                    type="text" 
                    className="search-bar" 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleSearch}
                    placeholder="Search by keywords to access the clothes you like" 
                />

                {/* Account Dropdown */}
                <div
                    className="account-container"
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
            </header>

            {/* Display uploaded image or prompt user to upload */}
            <div className="tryon-content">
                {uploadedImage ? (
                    <>
                        <button className="change-img-btn" onClick={() => navigate("/upload")}>Change Image</button>
                        <div className="tryon-display">
                            {/* Display uploaded image (result first)*/}
                            <img src={resultImage||uploadedImage} alt="Try on result" className="tryon-result-img" />
                        </div>
                        <div className="tryon-actions">
                            <button className="save-btn" onClick={handleSaveCombination}>Save Combination</button>
                            <button className="continue-btn" onClick={() => navigate("/download")}>Send to Email</button>
                        </div>
                    </>
                ) : (
                    <div className="upload-prompt">
                        <h2 className="tryon-placeholder">You haven't uploaded a full-body image yet.</h2>
                        <p>Please upload one now to start using the virtual dressing room.</p>
                        <button className="upload-btn" onClick={() => navigate("/upload")}>Upload Image</button>
                    </div>
                )}
            </div>

            {/* Sidebar */}
            <aside className="tryon-sidebar">
                <button className={`sidebar-btn ${activePanel === "closet" ? "active" : ""}`}
                        onClick={() => togglePanel("closet")}
                >
                    My Closet
                </button>
                <button className={"sidebar-btn"}
                        onClick={() => navigate(`/fullcloset?user_id=${userId}`)}
                >
                    View All Clothes
                </button>
                <button className={`sidebar-btn ${activePanel === "combinations" ? "active" : ""}`}
                        onClick={() => togglePanel("combinations")}
                >
                    Saved Combinations
                </button>
                <button className={`sidebar-btn ${activePanel === "recommendations" ? "active" : ""}`}
                        onClick={() => togglePanel("recommendations")}
                >
                    Explore Recommendations
                </button>
            </aside>

            {/* Closet Panel */}
            {activePanel === "closet" && (
                <div className="mycloset-panel">
                    <h3>My Try-On Closet</h3>
                    <select
                        className="mycloset-dropdown"
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                        <option value="tops">Tops</option>
                        <option value="dresses">Dresses</option>
                        <option value="bottoms">Bottoms</option>
                    </select>

                    {error && <p className="error-message">{error}</p>}

                    <ul className="mycloset-list">
                        {myCloset.length > 0 ? (
                            myCloset.map((item) => (
                                <li key={item.id} className="mycloset-item">
                                    <img src={item.url} alt="Clothing" className="mycloset-img"/>
                                        {/*added by zhihao Cao ---> generate the image button*/}
                                         <button className="generate-btn" onClick={(e) =>
                                            {
                                                if(isGenerating) {
                                                    window.alert("Please wait for the image to be generated");
                                                    e.stopPropagation();
                                                    return;
                                                }
                                                handleGenerateImage(item.id,item.url,item.category) /* Prevents the button from being clicked more than once*/
                                            }
                                        }
                                            disabled={isGenerating}
                                        >
                                            {isGenerating ? "Generating..." : "Tryon"}
                                        </button>

                                    {/*end*/}
                                    <button className="remove-btn" onClick={() => handleRemoveFromCloset(item.id)}>Remove</button>
                                </li>
                            ))
                        ) : (
                            <p>No items found for this category.</p>
                        )}
                    </ul>
                </div>
            )}

            {/* Combinations Panel */}
            {activePanel === "combinations" && (
                <div className="combination-panel">
                    <h3>My Combinations</h3>
                    <ul className="combination-list">
                        {combinations.length > 0 ? (
                            combinations.map((item) => (
                                <li key={item.id} className="combination-item">
                                  <img
                                    src={item.url}
                                    alt="combination"
                                    className="combination-img"
                                    onClick={() => setResultImage(item.url)}  
                                    style={{ cursor: "pointer" }}
                                  />
                                  <button
                                    className="remove-btn"
                                    onClick={() => handleDeleteCombination(item.id)}
                                  >
                                    Delete
                                  </button>
                                </li>
                              ))
                        ): (
                            <p>No saved combinations.</p>
                        )}
                    </ul>
                </div>
            )}

            {/* Recommendations Panel */}
            {activePanel === "recommendations" && (
                <div className="recommendations-panel">
                    <h3>People like you also prefer</h3>
                    <ul className="recommendation-list">
                        {recommendations.map((item) => (
                            <li key={item.id} className="recommendation-item" onClick={() => navigate(`/detail/${item.id}`, { state: { item }})}>
                                <img src={item.url} alt="recommends" className="recommendation-img"/>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

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
}

export default TryOn;
