import React from "react";
import Hero from "./Hero Section/Hero";
import MarketplacePreview from "./Market Place Preview/MarketPlacePreview";
import ValueSplit from "./Value Split Section/ValueSplit";
import Pillars from "./Pillars/Pillars";
import SocialProof from "./Social Proof/SocialProof";
import HowItWorks from "./How it works/HowItWorks";
import FinalCTA from "./Final CTA/FinalCTA";

export default function LandingPage() {
  return (
    <>
      <section className="landing-page-wrapper">
        <Hero />
        <MarketplacePreview />
        <ValueSplit />
        <Pillars/>
        <SocialProof/>
        <HowItWorks/>
        <FinalCTA/>
      </section>
    </>
  );
}
