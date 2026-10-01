import {
  Band,
  DayOnTheDock,
  Features,
  FinalCta,
  Hero,
  HowItWorks,
  IconStrip,
  LandingFooter,
  Nav,
  WhyQuai,
} from "../landing/sections.jsx";
import "../landing.css";

export default function Landing() {
  return (
    <div className="landing">
      <Nav />
      <main>
        <Hero />
        <HowItWorks />
        <Features />
        <Band />
        <IconStrip />
        <WhyQuai />
        <DayOnTheDock />
        <FinalCta />
      </main>
      <LandingFooter />
    </div>
  );
}
