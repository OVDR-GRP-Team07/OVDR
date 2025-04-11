/**
 * index.js - Entry point for the OVDR React application.
 *
 * @fileoverview Initializes the root React component and wraps it in a Router context.
 * Attaches the root to the HTML DOM. All routing and global styles begin from this file.
 *
 * @author
 * Peini SHE
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

/**
 * Create the root element for the app and render it inside the React Router context.
 */
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/*" element={<App />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
