import { Link, useNavigate } from "react-router-dom";
import { getRoleLabel, getRoleRoute } from "../api/client";

export default function Header() {
  const navigate = useNavigate();
  const isAuthenticated = localStorage.getItem("isAuthenticated") === "true";
  const userRole = localStorage.getItem("userRole");

  const handleLogout = () => {
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("token");
    navigate("/");
    window.location.reload();
  };

  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          Plateforme Conformité
        </Link>

        {isAuthenticated && (
          <div style={styles.profileSection}>
            <Link to={getRoleRoute(userRole)} style={styles.pageButton}>
              📄 {getRoleLabel(userRole)}
            </Link>
            <Link to="/profile" style={styles.profileLink}>
              👤 Profil
            </Link>
            <button style={styles.logoutButton} onClick={handleLogout}>
              🚪 Se déconnecter
            </button>
          </div>
        )}
      </div>
    </header>
  );
}

const styles = {
  profileSection: { display: "flex", alignItems: "center", gap: "0.5rem", marginLeft: "auto" },
  pageButton: { fontSize: "13px", color: "#0f766e", fontWeight: "500", textDecoration: "none", padding: "6px 12px", borderRadius: "6px", border: "1px solid #0f766e" },
  profileLink: { fontSize: "13px", color: "#0f766e", fontWeight: "500", textDecoration: "none", padding: "6px 12px", borderRadius: "6px", border: "1px solid #b2dfdb" },
  logoutButton: { fontSize: "13px", color: "#c62828", fontWeight: "500", padding: "6px 12px", borderRadius: "6px", border: "1px solid #ef5350", backgroundColor: "transparent", cursor: "pointer" },
};
