import React, { useState } from "react";
import "../styles/landingPage.css"
import "./Hero.css"
import { TfiMenuAlt } from "react-icons/tfi";
import { StyledLogo } from "../../Login/Login";


export default function Hero() {
    const [menuOpen,setMenuOpen]= useState(false)
  return (
    <section className="hero-template">

      {/* NAVBAR */}
      <div className="navbar">
        <div className="container navbar-inner">

          {/* LEFT SIDE */}
          <div className="nav-left">

            {/* <div className="logo">Ouranious</div> */}
            <StyledLogo></StyledLogo>
          </div>

          {/* DESKTOP NAV */}
          <div className="nav-group desktop-nav">
            <div className="nav-links-nav">
              <a href="#marketplace">Marketplace</a>
              <a href="#news">News</a>
              <a href="#about">About</a>
            </div>

            <div className="nav-actions">
              <a href="/login" className="nav-login">Login</a>

              <a href="/create_account" className="nav-cta">
                Create Profile
              </a>
            </div>
          </div>

          {/* MOBILE CTA */}
          <div className="mobile-cta">
            <a href="/create_account" className="nav-cta">
              Sign Up
            </a>
          </div>

        </div>
      </div>

      {/* MOBILE DRAWER */}
      {menuOpen && (
        <div className="mobile-menu-overlay" onClick={() => setMenuOpen(false)}>
          <div
            className="mobile-drawer"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="drawer-header">
              <span className="logo">Ouranious</span>
              <button
                className="close-btn"
                onClick={() => setMenuOpen(false)}
              >
                ✕
              </button>
            </div>

            <div className="drawer-links">
              <a href="#marketplace">Marketplace</a>
              <a href="#">News</a>
              <a href="#about">About</a>
              <a href="/login">Login</a>
            </div>
          </div>
        </div>
      )}

      <button
              className="hamburger-icon"
              onClick={() => setMenuOpen(true)}
            >
              
              <span className="menu-only">
                <TfiMenuAlt/>
                <span className="menu-text">
                  Menu
                </span>
              </span>
            </button>

      {/* HERO */}
      <div className="hero">
        
        <div className="container hero-grid">

          {/* LEFT */}
          <div>
            <h1 className="hero-title">
              Build, Showcase, and Grow Your Startup with Ouranious
            </h1>

            <p className="hero-sub">
              Ouranious is Africa’s startup marketplace where founders promote
              their businesses, reach new customers, and access the tools they
              need to grow.
            </p>

            <div className="hero-actions">
              <a href="/signup" className="btn-primary-1">
                Create Your Startup Profile
              </a>

              <a href="/marketplace" className="btn-secondary-1">
                Explore the Marketplace
              </a>
            </div>

            <p className="hero-trust">
              Join founders from across Africa building the future of business.
            </p>
          </div>

          {/* RIGHT */}
          <div className="hero-image">
            <img
              src="https://eu-images.contentstack.com/v3/assets/blta47798dd33129a0c/blt2dd0b8c605cf0a51/681de36599efa190ae7fa0ea/startup_employees_1_%281%29.jpg"
              alt="African entrepreneur building a startup"
            />
          </div>

        </div>
      </div>

    </section>
  );
}
