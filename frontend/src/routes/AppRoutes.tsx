// src/routes/AppRoutes.tsx

import { Routes, Route, Navigate } from "react-router-dom";
import EntryRouter from "./EntryRouter";

import Onboarding from "../pages/Onboarding/Onboarding";
import Main from "../pages/Main/Main";
import Interview from "../pages/Interview/Interview";
import Result from "../pages/Result/Result"; 

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<EntryRouter />} />
      <Route path="/onboarding" element={<Onboarding />} />
      <Route path="/main" element={<Main />} />
      <Route path="/interview" element={<Interview />} />
      <Route path="/result" element={<Result />} />

      {/* fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}