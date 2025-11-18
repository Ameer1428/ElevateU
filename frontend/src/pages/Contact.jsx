import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Contact.css';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert("Thank you for your message! We will respond soon.");
    setFormData({ name: '', email: '', subject: '', message: '' });
  };

  return (
    <div className="contact-app">
      <header className="header">
        <div className="container header-bar">
          <div className="logo">
            <Link to="/"><h2>ElevateU</h2></Link>
          </div>
        </div>
      </header>

      <section className="contact-hero">
        <div className="container">
          <div className="hero-content">
            <h1>Get In Touch</h1>
            <p>We’d love to hear from you. Send us a message and we will reply soon.</p>
          </div>
        </div>
      </section>

      <section className="contact-content">
        <div className="container contact-grid">
          
          <div className="contact-info">
            <h2>Contact Information</h2>

            <div className="contact-item">
              <div className="contact-icon">📧</div>
              <div>
                <h3>Email</h3>
                <p>support@elevateu.com</p>
              </div>
            </div>

            <div className="contact-item">
              <div className="contact-icon">📞</div>
              <div>
                <h3>Phone</h3>
                <p>+1 (555) 123-4567</p>
              </div>
            </div>

            <div className="contact-item">
              <div className="contact-icon">📍</div>
              <div>
                <h3>Address</h3>
                <p>123 Education Street<br />Learning City, LC 12345</p>
              </div>
            </div>

            <div className="contact-item">
              <div className="contact-icon">🕒</div>
              <div>
                <h3>Business Hours</h3>
                <p>Mon–Fri: 9 AM – 6 PM<br />Sat: 10 AM – 4 PM</p>
              </div>
            </div>
          </div>

          <div className="contact-form-container">
            <h2>Send Us a Message</h2>

            <form className="contact-form" onSubmit={handleSubmit}>
              <input
                type="text"
                name="name"
                placeholder="Your Name"
                value={formData.name}
                onChange={handleChange}
                required
              />

              <input
                type="email"
                name="email"
                placeholder="Your Email"
                value={formData.email}
                onChange={handleChange}
                required
              />

              <input
                type="text"
                name="subject"
                placeholder="Subject"
                value={formData.subject}
                onChange={handleChange}
                required
              />

              <textarea
                name="message"
                placeholder="Your Message"
                rows="5"
                value={formData.message}
                onChange={handleChange}
                required
              ></textarea>

              <button type="submit" className="submit-btn">Send Message</button>
            </form>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="container">
          <p>© 2025 ElevateU. All rights reserved.</p>
        </div>
      </footer>

    </div>
  );
};

export default Contact;
