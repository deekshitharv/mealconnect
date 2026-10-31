import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import LoadingSpinner from "./LoadingSpinner";

// Only logged-in users get through. Everyone else is sent to /login.
export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <LoadingSpinner label="Checking your session..." />;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  return children;
}