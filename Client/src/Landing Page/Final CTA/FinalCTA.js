import "./FinalCTA.css";
import React from "react";
import "../styles/landingPage.css";

export default function FinalCTA() {
  return (
    <section className="final-cta">
      <div className="container cta-inner">

        <h2>Africa’s Next Great Startup Could Be Yours</h2>

        <p>
          Join Ouranious today and start building, showcasing, and growing your business
          with a community that believes in African innovation.
        </p>

        <div className="cta-actions">
          <a href="/signup" className="btn-primary-1">
            Create Your Startup Profile
          </a>

          <a href="/marketplace" className="btn-secondary-1">
            or explore the marketplace
          </a>
        </div>

      </div>
    </section>
  );
}