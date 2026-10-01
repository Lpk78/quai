import { Route, Routes } from "react-router-dom";

import { ScannedParcelProvider } from "./scan/scannedParcel.jsx";

import Landing from "./pages/Landing.jsx";
import AppShell from "./pages/AppShell.jsx";
import Home from "./pages/Home.jsx";
import Scan from "./pages/Scan.jsx";
import Dictate from "./pages/Dictate.jsx";
import PlanScreen from "./pages/PlanScreen.jsx";
import NotFound from "./pages/NotFound.jsx";

export default function App() {
  return (
    <ScannedParcelProvider>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/app" element={<AppShell />}>
          <Route index element={<Home />} />
          <Route path="scan" element={<Scan />} />
          <Route path="dictate" element={<Dictate />} />
        </Route>
        <Route path="/app/plan" element={<PlanScreen />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </ScannedParcelProvider>
  );
}
