import React from "react";
import StartupCard from "./StartupCard";
import "../styles/landingPage.css";
import "./MarketPlacePreview.css"

export default function MarketplacePreview() {

  const startups = [
    {
      name: "AgriNova",
      tagline: "Smart solutions for small-scale farmers",
      category: "AgriTech",
      country: "Kenya",
      image: "https://media.newyorker.com/photos/590977fcebe912338a377f20/master/pass/Bright-TheRaceforAfricanE-Commerce.jpg"
    },
    {
      name: "PayLink Africa",
      tagline: "Simple digital payments for local businesses",
      category: "Fintech",
      country: "Nigeria",
      image: "https://plus.unsplash.com/premium_photo-1682096368453-e6e9d663acc9?fm=jpg&ixid=M3wxMjA3fDB8MHxwaG90by1yZWxhdGVkfDE2fHx8ZW58MHx8fHx8&ixlib=rb-4.1.0&q=60&w=3000"
    },
    {
      name: "Zuri Fashion",
      tagline: "Modern African fashion for global markets",
      category: "Fashion",
      country: "South Africa",
      image: "https://elements-resized.envatousercontent.com/envato-dam-assets-production/EVA/TRX/a4/c0/46/ad/fa/v1_E10/E10929J2.jpg?w=800&cf_fit=scale-down&mark-alpha=18&mark=https%3A%2F%2Felements-assets.envato.com%2Fstatic%2Fwatermark4.png&q=85&format=auto&s=16ba26b038a9613eaf0ba6531f61b132701240aed63f5cace090e884c7dc143e"
    }
  ];

  return (
    <section className="marketplace-section" id="marketplace">
      <div className="container">

        {/* HEADER */}
        <div className="section-header">
          <h2>Discover What Africa Is Building</h2>
          <p>
            Explore startups, small businesses, and innovative services from founders across the continent.
          </p>
        </div>

        {/* GRID */}
        <div className="startup-grid">
          {startups.map((startup, index) => (
            <StartupCard key={index} data={startup} />
          ))}
        </div>

        {/* CTA */}
        <div className="section-cta">
          <a href="/marketplace" className="btn-primary-1">
            Explore Full Marketplace →
          </a>
        </div>

      </div>
    </section>
  );
}