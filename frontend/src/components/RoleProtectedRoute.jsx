import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { homeFor } from "../utils/roles";
import LoadingSpinner from "./LoadingSpinner";

// Logged in AND the right role. A wrong role is sent to their own dashboard.
export default function RoleProtectedRoute({ roles, children }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <LoadingSpinner label="Checking your session..." />;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  if (!roles.includes(user.role)) return <Navigate to={homeFor(user.role)} replace />;
  return children;
}