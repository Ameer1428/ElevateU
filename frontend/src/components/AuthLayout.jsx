import React from "react";
import "./auth.css";

export default function AuthLayout({ title, children }) {
  return (
    <div className="auth-page">
      <div className="auth-card" aria-label={title}>
        {/* Optional title/header above Clerk UI */}
        {title && (
          <header style={{ marginBottom: "1rem" }}>
            <h1 style={{ margin: 0 }}>{title}</h1>
          </header>
        )}
        <div>
          {children}
        </div>
      </div>
    </div>
  );
}
