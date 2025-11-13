// src/components/Footer.jsx
import React from "react";

export default function Footer() {
  const footerStyle = {
    marginTop: "3rem",
    padding: "1.5rem 1rem",
    background: "rgba(10,25,41,0.95)",
    color: "white",
    borderRadius: "10px",
    display: "flex",
    flexDirection: "column",
    gap: "0.6rem",
    alignItems: "center",
    textAlign: "center",
    fontFamily: "sans-serif",
  };

  const smallText = {
    fontSize: "0.9rem",
    opacity: 0.9,
  };

  const tagsStyle = {
    display: "flex",
    gap: "1rem",
    fontSize: "1rem",
    fontWeight: 600,
    opacity: 0.95,
  };

  return (
    <footer style={footerStyle}>
      <div style={smallText}>© {new Date().getFullYear()} ElevateU</div>

      <div style={tagsStyle}>
        <span>AI Learning</span>
        <span>Smart Courses</span>
      </div>
    </footer>
  );
}
