import "./ValueSplit.css"
import React from "react";
import "../styles/landingPage.css";
import { GrCheckboxSelected } from "react-icons/gr";

export default function ValueSplit() {
    const foundersCapabilities= [
        "Create your startup profile",
        "Promote your products and services",
        "Reach customers across Africa and beyond",
        "Access tools to grow your business"
    ]
    const supportersCapabilities = [
        "Discover African startups",
        "Support local businesses",
        "Find products and services from real founders",
        "Stay informed on emerging businesses"
    ]

  return (
    <section className="value-section">
      <div className="container">

        {/* HEADER */}
        <div className="section-header">
          <h2>Built for Founders. Designed for Growth.</h2>
          <p>
            Whether you're building a startup or supporting African businesses,
            Ouranious connects you to opportunity.
          </p>
        </div>

        {/* SPLIT */}
        <div className="value-grid">

          {/* FOUNDERS */}
          <div className="value-card">
            <h3>For Founders</h3>

            <ul>
              {foundersCapabilities.map((capability, index) => (

                <div key={index} className="capability-list-landing">
                    <span className="check-icon"><GrCheckboxSelected  /></span>
                  
                  <li className="cap-li">{capability}</li>
                </div>
              ))}
            </ul>

            <a href="/signup" className="btn-primary-1">
              Create Your Startup Profile →
            </a>
          </div>

          {/* SUPPORTERS */}
          <div className="value-card">
            <h3>For Supporters</h3>

            <ul>
              {supportersCapabilities.map((capability, index) => (
                <div key={index} className="capability-list-landing">
                    <span className="check-icon"><GrCheckboxSelected  /></span>
                  
                  <li className="cap-li">{capability}</li>
                </div>
              ))}
            </ul>

            <a href="/marketplace" className="btn-secondary-1">
              Explore the Marketplace →
            </a>
          </div>

        </div>

      </div>
    </section>
  );
}

