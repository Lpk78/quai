import {
  DayOnTheDock,
  Features,
  FinalCta,
  Hero,
  HowItWorks,
  IconStrip,
  LandingFooter,
  LoadingPlanReady,
  Nav,
  NavyBanner,
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
        <NavyBanner />
        <RouteOrder />
        <IconStrip />
        <WhyQuai />
        <DayOnTheDock />
        <FinalCta />
      </main>
      <LandingFooter />
    </div>
  );
}
