import "./SocialProof.css";
import React from "react";
import "../styles/landingPage.css";

export default function SocialProof() {

  const testimonials = [
    {
      name: "Daniel K.",
      role: "AgriTech Founder",
      quote:
        "Ouranious gives small founders like me a place to showcase what we are building.",
      image: "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/42/11/b3/5e/dc/v1_E11/E114H91P.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=0f9e17645f27d3c7506fc796be89791a73264d612bb1ef94163a58a0a8911f1e"
    },
    {
      name: "Amina S.",
      role: "Fashion Entrepreneur",
      quote:
        "I’ve always wanted a platform focused on African startups. This is exactly that.",
      image: "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/2f/4f/9a/70/3f/v1_E10/E102BB1W.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=91ada54cdd090d6283783c890c2f5b50d8c68b6c1364dd83d16fe2550b915378"
    },
    {
      name: "Michael T.",
      role: "Small Business Supporter",
      quote:
        "Discovering new African businesses in one place is powerful.",
      image: "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/e3/85/47/bb/93/v1_E10/E101QFO5.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=8eb03dbf9a3797edb615a32ac516cab6093c932a6e1f2a08c184bd6f0bb64848"
    }
  ];

  return (
    <section className="social-section">
      <div className="container">

        {/* HEADER */}
        <div className="section-header">
          <h2>Trusted by Emerging African Founders</h2>
          <p>
            Ouranious is building a community of ambitious entrepreneurs across the continent.
          </p>
        </div>

        {/* TESTIMONIALS */}
        <div className="testimonial-grid">
          {testimonials.map((t, index) => (
            <div key={index} className="testimonial-card">

              <div className="testimonial-top">
                <img src={t.image} alt={t.name} />
              </div>

              <p className="testimonial-quote">
                “{t.quote}”
              </p>

              <div className="testimonial-author">
                <strong>{t.name}</strong>
                <span>{t.role}</span>
              </div>

            </div>
          ))}
        </div>

        {/* COMMUNITY LINE */}
        <div className="community-line">
          Join a growing network of founders building the future of African business.
        </div>

      </div>
    </section>
  );
}