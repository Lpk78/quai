import {
  DayOnTheDock,
  Features,
  FinalCta,
  FooterBand,
  Hero,
  HowItWorks,
  IconStrip,
  LoadingPlanReady,
  Nav,
  RouteOrder,
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
        <LoadingPlanReady />
        <RouteOrder />
        <IconStrip />
        <WhyQuai />
        <DayOnTheDock />
        <FinalCta />
      </main>
      <FooterBand />
    </div>
  );
}
