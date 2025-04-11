/**
 * App.js - Main routing component of the Online Virtual Dressing Room (OVDR) system.
 *
 * @fileoverview Defines application-level routes and global state management for user identity,
 * uploaded images, and generated try-on results.
 *
 * Each route maps to a distinct user-facing page such as login, registration, virtual try-on, and closet history.
 * Global state includes image data and user session information used across different components.
 *
 * @author
 * Peini SHE
 */

import { Routes, Route } from 'react-router-dom';
import { useState } from "react";
import './App.css';
import Login from "./Login";
import Register from "./Register";
import Home from "./Home";
import TryOn from "./TryOn";
import UploadImage from "./UploadImage";
import History from "./History"
import FullCloset from "./FullCloset"
import ClothesDetail from "./ClothesDetail";
import SendImage from './SendImage';

/**
 * App - Main entry point of the frontend routing structure.
 *
 * This component defines client-side routing paths using React Router.
 * It also maintains shared application state such as current user, uploaded images, and results.
 *
 * @component
 * @returns {JSX.Element} A React element that defines all routes of the application.
 */
function App() {
  /**
   * State to hold the image uploaded by the user.
   * @type {Array<string|null|Function>}
   */
  const [uploadedImage, setUploadedImage] = useState(null);

  /**
   * State to store the currently logged-in username.
   * @type {Array<string|Function>}
   */
  const [username, setUsername] = useState(localStorage.getItem("username") || "");

  /**
   * State to store the result image after try-on processing.
   * @type {Array<string|null|Function>}
   */
  const [resultImage, setResultImage] = useState(null);

  /**
   * State to hold user identifier, synced from localStorage.
   * @type {Array<string|null|Function>}
   */
  const [userId, setUserId] = useState(localStorage.getItem("user_id") || null);

  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login setUserId={setUserId} setUsername={setUsername} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/tryon" element={
          <TryOn
            userId={userId}
            username={username}
            uploadedImage={uploadedImage}
            setUploadedImage={setUploadedImage}
            resultImage={resultImage}
            setResultImage={setResultImage}
          />}
        />
        <Route path="/upload" element={
          <UploadImage
            uploadedImage={uploadedImage}
            setUploadedImage={setUploadedImage}
            userId={userId}
          />}
        />
        <Route path="/history" element={<History userId={userId} username={username} />} />
        <Route path="/fullcloset" element={<FullCloset userId={userId} username={username} />} />
        <Route path="/detail/:id" element={<ClothesDetail userId={userId} />} />
        <Route path="/download" element={<SendImage resultImage={resultImage} />} />
      </Routes>
    </div>
  );
}

export default App;