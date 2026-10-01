import { Route, Routes } from "react-router-dom";

import Landing from "./pages/Landing.jsx";
import Login from "./pages/Login.jsx";
import AppShell from "./pages/AppShell.jsx";
import Home from "./pages/Home.jsx";
import Dictate from "./pages/Dictate.jsx";
import PlanScreen from "./pages/PlanScreen.jsx";
import NotFound from "./pages/NotFound.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/app" element={<AppShell />}>
        <Route index element={<Home />} />
        <Route path="dictate" element={<Dictate />} />
      </Route>
      <Route path="/app/plan" element={<PlanScreen />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
