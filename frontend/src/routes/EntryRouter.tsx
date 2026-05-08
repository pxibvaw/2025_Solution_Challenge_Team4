// src/routes/EntryRouter.tsx

import { Navigate } from "react-router-dom";
import { isOnboarded } from "../store/profileStore";

export default function EntryRouter() {
  // onboarded === true -> /main
  // 아니면 -> /onboarding
  return isOnboarded() ? <Navigate to="/main" replace /> : <Navigate to="/onboarding" replace />;
}