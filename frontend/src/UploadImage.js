/**
 * UploadImage.js - Upload or capture a full-body image for virtual try-on.
 *
 * @fileoverview Allows users to preview an image (from camera or file),
 * confirm submission, and upload to backend. Delays global state changes
 * until the user confirms submission.
 *
 * @author
 * Peini SHE & Zixin DING
 * 
 */

 /* Purpose:
 * - Allow users to upload or capture full-body images
 * - Preview before upload, avoid immediate state changes
 * - Upload image to backend only after confirmation
 * - Prevent overwriting previous image if "Exit" is clicked
 * - Cache-busting via ?t=timestamp to force image refresh
 * 
 * Modifications by Zixin Ding:
 * - Decoupled preview and upload logic
 * - Delayed backend upload until Submit
 * - Added imageSource to track origin (camera/file)
 * - Prevented global state overwrite on cancel
 * - Fixed image caching issues using timestamp URL
 */

import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./UploadImage.css";
import Webcam from "react-webcam";

function UploadImage({ uploadedImage, setUploadedImage, userId}) {
    const navigate = useNavigate();
    const [imagePreview, setImagePreview] = useState(null);
    const previousImageRef = useRef(uploadedImage);
    const [cameraOpen, setCameraOpen] = useState(false);
    const webcamRef = useRef(null);
    // Track where the image came from
    const [imageSource, setImageSource] = useState(null); // "camera" | "file"
    
    useEffect(() => {
        if (cameraOpen) {
            console.log("Camera Open.");
        } else {
            console.log("Camera Closed.");
        }
    }, [cameraOpen]);

    /**
     * Handle file input and preview the image without uploading.
     * @param {React.ChangeEvent<HTMLInputElement>} event
     */
    const handleImageUpload = async (event) => {
        const file = event.target.files[0];
        if (file) {
            setCameraOpen(false);  // Make sure camera closes
            setImageSource("file");  // Set source flag

            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = async () => {
                const base64String = reader.result;
                setImagePreview(base64String);  // Just preview
            };
        }
    };

    /**
     * Capture a photo from the webcam and preview it.
     */
    const capturePhoto = async () => {
        if (webcamRef.current) {
            const imageSrc = webcamRef.current.getScreenshot();
            setImagePreview(imageSrc);
            setImageSource("camera"); 
            setCameraOpen(false);
        }
    };

    /**
     * Upload the confirmed image file to the backend server.
     * @param {File} file - The image file to be uploaded
     * @returns {Promise<string|undefined>} - Uploaded image URL if successful
     */
    // UPDATED: This only runs when user clicks "Submit"
    const uploadToBackend = async (file) => {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("user_id", userId);

        try {
            // const response = await fetch("http://localhost:5000/upload_image", {
            //     method: "POST",
            //     body: formData,
            // });

            const response = await fetch("/upload_image", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            if (response.ok) {
                // NEW: Full image URL with timestamp to prevent caching
                const fullImageUrl = `http://localhost:5000/${data.image_path.replace(/\\/g, "/")}?t=${Date.now()}`;
                console.log("Uploaded Image URL:", fullImageUrl);
                return fullImageUrl;
            } else {
                console.error("Upload failed:", data.error);
            }
        } catch (error) {
            console.error("Error uploading image:", error);
        }
    };

    /**
     * On user confirmation, convert preview to file and send to backend.
     */
    // NEW: Only upload and update when user clicks "Submit"
    const handleSubmit = async () => {
        if (!imagePreview) return;
    
        try {
            const blob = await fetch(imagePreview).then(res => res.blob());
            const file = new File([blob], "submitted_image.jpg", { type: "image/jpeg" });
    
            const uploadedUrl = await uploadToBackend(file);
            if (uploadedUrl) {
                setUploadedImage(uploadedUrl);  // Set global state with backend image path  
                navigate("/tryon");  // Navigate only after success
            } else {
                alert("Image upload failed.");
            }
            
        } catch (error) {
            console.error("Failed to submit image:", error);
            alert("Failed to upload image. Please try again.");
        }
    };
    
    /**
     * Exit preview mode, revert to previous uploaded image.
     */
    const handleExit = () => {
        setImagePreview(previousImageRef.current);
        setUploadedImage(previousImageRef.current);
        navigate(-1);
    };

    return (
        <div className="upload-container">
            <h1>Upload or Capture a Photo</h1>

            {!imagePreview && !cameraOpen && (
                <div className="upload-options">
                    <button className="upload-btn" onClick={() => setCameraOpen(true)}>📷 Use Camera</button>
                    <label className="upload-btn">
                        📁 Upload Image
                        <input type="file" accept="image/*" onChange={handleImageUpload} hidden />
                    </label>
                </div>
            )}

            {cameraOpen && (
                <div className="camera-container" >
                    <Webcam
                        audio={false}
                        ref={webcamRef}
                        screenshotFormat="image/png"
                        className="webcam-view"
                        videoConstraints={{
                            width: 384,
                            height: 512,
                            facingMode: "user", // front-facing camera
                        }}
                    />
                    <div className="button-row">
                    <button className="exit-btn" onClick={handleExit}>Exit</button>
                    <button className="action-btn" onClick={capturePhoto}>Capture</button>
                    </div>
                </div>
            )}

            {imagePreview && (
                <div className="preview-container">
                    <img src={imagePreview} 
                        alt="Preview" 
                        className="preview-image"
                        key={imagePreview}  />
                    <div className="button-row">
                        <button className="exit-btn" onClick={handleExit}>Exit</button>
                        <button className="action-btn" onClick={handleSubmit}>Submit</button>
                    </div>
                </div>
            )}    
        </div>
    );
}

export default UploadImage;
