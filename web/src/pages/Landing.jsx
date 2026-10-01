import {
  Band,
  DayOnTheDock,
  Features,
  FinalCta,
  Hero,
  HowItWorks,
  LandingFooter,
  Nav,
  WhyQuai,
} from "../landing/sections.jsx";
import "../landing.css";
import "../phone.css";

export default function Landing() {
  return (
    <div className="landing">
      <Nav />
      <main>
        <Hero />
        <HowItWorks />
        <Features />
        <Band />
        <WhyQuai />
        <DayOnTheDock />
        <FinalCta />
      </main>
      <LandingFooter />
    </div>
  );
}
