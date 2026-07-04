import "./Pillars.css"
import React from "react";
import "../styles/landingPage.css";

export default function Pillars() {
  return (
    <section className="pillars-section">
      <div className="container">

        {/* HEADER */}
        <div className="section-header">
          <h2>The Ouranious Ecosystem</h2>
          <p>
            A unified platform built to help African founders build, promote, and fund their startups.
          </p>
        </div>

        {/* PILLARS GRID */}
        <div className="pillars-grid">

          {/* MARKETPLACE */}
          <div className="pillar-card">
            <div className="pillar-icon">🛍️</div>
            <h3>Marketplace</h3>
            <p>
              Showcase your startup, promote your products and services,
              and reach customers across Africa and beyond.
            </p>
          </div>

          {/* NEWS */}
          <div className="pillar-card">
            <div className="pillar-icon">📰</div>
            <h3>Ouranious News</h3>
            <p>
              Learn from real founder stories, business insights, and
              opportunities shaping the African startup landscape.
            </p>
          </div>

          {/* INVESTMENT */}
          <div className="pillar-card">
            <div className="pillar-icon">💼</div>
            <h3>Investment</h3>
            <p>
              Connect promising startups with investors and unlock
              opportunities for funding and growth.
            </p>
          </div>

        </div>

      </div>
    </section>
  );
}