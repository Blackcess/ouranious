import "./HowItWorks.css";
import React from "react";
import "../styles/landingPage.css";

export default function HowItWorks() {
  return (
    <section className="how-section">
      <div className="container">

        {/* HEADER */}
        <div className="section-header">
          <h2>How Ouranious Works</h2>
          <p>
            Get started in minutes and begin growing your startup today.
          </p>
        </div>

        {/* STEPS */}
        <div className="steps-grid">

          {/* STEP 1 */}
          <div className="step-card">
            <div className="step-number">01</div>
            <h3>Create Your Profile</h3>
            <p>
              Sign up and create your startup profile to introduce your business to the community.
            </p>
          </div>

          {/* STEP 2 */}
          <div className="step-card">
            <div className="step-number">02</div>
            <h3>Showcase Your Business</h3>
            <p>
              Publish your products or services and make your startup visible to customers and supporters.
            </p>
          </div>

          {/* STEP 3 */}
          <div className="step-card">
            <div className="step-number">03</div>
            <h3>Grow and Connect</h3>
            <p>
              Reach new customers, connect with other founders, and unlock growth opportunities.
            </p>
          </div>

        </div>

        {/* CTA */}
        <div className="section-cta">
          <a href="/signup" className="btn-primary-1">
            Get Started Today →
          </a>
        </div>

      </div>
    </section>
  );
}