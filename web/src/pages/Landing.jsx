import {
  DayOnTheDock,
  Features,
  FinalCta,
  FooterBand,
  Hero,
  HowItWorks,
  IconStrip,
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
        <IconStrip />
        <WhyQuai />
        <DayOnTheDock />
        <FinalCta />
      </main>
      <FooterBand />
    </div>
  );
}
