import React from 'react';
import { Link } from 'react-router-dom';
import './About.css';

const About = () => {

  const teamMembers = [
    { name: "Ameer", role: "Founder & CEO", bio: "10+ years in EdTech", avatar: "👨‍💼" },
    { name: "Dhanush", role: "Head of Instruction", bio: "Former Google Lead Instructor", avatar: "🧑‍🎓" },
    { name: "Venkatesh", role: "CMO", bio: "Expert in Learning Platforms", avatar: "🦹‍♂️" },
    { name: "Azad", role: "CTO", bio: "Expert in AI with 15 Years", avatar: "🧑‍💻" },
    { name: "Teja", role: "Team Leader", bio: "Leads TO SOLVE IT Problems", avatar: "🦸‍♂️" },
    { name: "Srujan", role: "Tutor", bio: "Teaches several Techs", avatar: "👨‍💻" }
  ];

  return (
    <div className="about-app">
      {/* NAVBAR */}
      <header className="header">
        <div className="container header-bar">
          <div className="logo">
            <Link to="/"><h2 className='elevateu' style={{color:"#00294b"}}>ElevateU</h2></Link>
          </div>
        </div>
      </header>

      {/* HERO */}
      <section className="about-hero">
        <div className="container">
          <div className="hero-content">
            <h1 style={{color:"#00294b"}}>About ElevateU</h1>
            <p>Transforming education through innovative learning solutions</p>
          </div>
        </div>
      </section>

      {/* CONTENT */}
      <section className="about-content">
        <div className="container">

          <div className="about-section">
            <h2 style={{color:"#00294b"}}>Our Mission</h2>
            <p>
              At ElevateU, we believe that education should be accessible, engaging, and transformative. 
              Our mission is to bridge the gap between traditional education and industry requirements, 
              providing students with real-world skills that prepare them for successful careers.
            </p>
          </div>

          <div className="about-section">
            <h2 style={{color:"#00294b"}}>Our Story</h2>
            <p>
              Founded in 2020, ElevateU began as a small initiative to help students build practical skills.
              Today, we serve thousands of learners worldwide with a commitment to quality instruction,
              personalized support, and student success.
            </p>
          </div>

          <div className="about-section">
            <h2 style={{color:"#00294b"}}>What Makes Us Different</h2>

            <div className="features-grid">
              <div className="feature">
                <div className="feature-icon">🎯</div>
                <h3 style={{color:"#00294b"}}>Industry-Focused</h3>
                <p>Courses crafted with real industry needs in mind.</p>
              </div>

              <div className="feature">
                <div className="feature-icon">🤝</div>
                <h3 style={{color:"#00294b"}}>Personalized Support</h3>
                <p>One-on-one mentorship and expert guidance.</p>
              </div>

              <div className="feature">
                <div className="feature-icon">💼</div>
                <h3 style={{color:"#00294b"}}>Career Services</h3>
                <p>Resume reviews, interview prep, and job-ready training.</p>
              </div>
            </div>
          </div>

          <div className="about-section">
            <h2 style={{color:"#00294b"}}>Meet Our Team</h2>

            <div className="team-grid">
              {teamMembers.map((member, index) => (
                <div key={index} className="team-card">
                  <div className="team-avatar">{member.avatar}</div>

                  <h3 style={{color:"#00294b"}}>{member.name}</h3>
                  <p className="team-role">{member.role}</p>
                  <p className="team-bio">{member.bio}</p>
                </div>
              ))}
            </div>
          </div>

        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <div className="container">
          <p>© 2025 ElevateU. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default About;