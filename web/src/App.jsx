import { Route, Routes } from "react-router-dom";

import Landing from "./pages/Landing.jsx";
import AppShell from "./pages/AppShell.jsx";
import NotFound from "./pages/NotFound.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/app" element={<AppShell />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
