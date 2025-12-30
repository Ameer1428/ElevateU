import { Link } from "react-router-dom";
import React from "react";
import './Footer.css';

export default function Footer() {
  return (
    <footer className="site-footer" role="contentinfo">

  {/* Giant background word */}
  <div className="giant-brand" style={{color:"white"}} aria-hidden>
    ElevateU
  </div>

  {/* Visible centered content */}
  <div className="footer-center">
    <Link to="/about" className="footer-link">About</Link>
    <Link to="/contact" className="footer-link">Contact</Link>
  </div>

</footer>
  );
}



