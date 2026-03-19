import { Navigate } from "react-router-dom";

// Backend roles: operator | supplier | admin
export default function ProtectedRoute({ children, allowedRole }) {
  const isAuthenticated = localStorage.getItem("isAuthenticated");
  const userRole = localStorage.getItem("userRole");

  if (isAuthenticated !== "true") {
    return <Navigate to="/login" replace />;
  }

  if (allowedRole && userRole !== allowedRole) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
