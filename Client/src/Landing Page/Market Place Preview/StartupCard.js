import React from "react";
import "../styles/landingPage.css";
import "./StartupCard.css"

export default function StartupCard({ data }) {
  return (
    <div className="startup-card">

      <div className="startup-image">
        <img src={data.image} alt={data.name} />
      </div>

      <div className="startup-content">
        <h3>{data.name}</h3>
        <p className="tagline">{data.tagline}</p>

        <div className="meta">
          <span className="pill">{data.category}</span>
          <span className="country">{data.country}</span>
        </div>

        <div className="view-link">
          View Profile →
        </div>
      </div>

    </div>
  );
}
