import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { getRoleLabel } from "../api/client";

export default function ProfilePage() {
  const navigate = useNavigate();
  const [userEmail] = useState(localStorage.getItem("userEmail") || "");
  const userRole = localStorage.getItem("userRole");

  const handleLogout = () => {
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <div className="page">
      <div className="card card-md">
        <div style={styles.header}>
          <h2>👤 Mon profil</h2>
          <p>Informations de votre compte.</p>
        </div>

        <div style={styles.profileInfo}>
          <div style={styles.infoCard}>
            <label style={styles.label}>Email</label>
            <div style={styles.value}>{userEmail || "Non défini"}</div>
          </div>
          <div style={styles.infoCard}>
            <label style={styles.label}>Rôle</label>
            <div style={styles.value}>{getRoleLabel(userRole)}</div>
          </div>
        </div>

        <div style={styles.actions}>
          <button style={styles.logoutButton} onClick={handleLogout}>
            🚪 Se déconnecter
          </button>
        </div>

        <Link className="back-link" to="/">← Retour à l'accueil</Link>
      </div>
    </div>
  );
}

const styles = {
  header: { marginBottom: "2rem", borderBottom: "2px solid #e0f2f1", paddingBottom: "1.5rem" },
  profileInfo: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem", marginBottom: "2rem" },
  infoCard: { padding: "1.5rem", backgroundColor: "#f0fffe", border: "1px solid #b2dfdb", borderRadius: "8px" },
  label: { display: "block", fontSize: "0.875rem", color: "#00695c", fontWeight: "600", marginBottom: "0.5rem" },
  value: { fontSize: "1rem", color: "#0f766e", fontWeight: "500" },
  actions: { display: "flex", gap: "1rem", marginBottom: "1.5rem" },
  logoutButton: { padding: "0.75rem 1.5rem", backgroundColor: "#c62828", color: "white", border: "none", borderRadius: "6px", fontSize: "0.95rem", fontWeight: "600", cursor: "pointer" },
};
