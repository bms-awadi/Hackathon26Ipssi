import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register, getRoleRoute } from "../api/client";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("operator");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await register(email, password, role);
      if (data.token) {
        localStorage.setItem("token", data.token);
        localStorage.setItem("isAuthenticated", "true");
        localStorage.setItem("userRole", data.user.role);
        localStorage.setItem("userEmail", data.user.email);
        navigate(getRoleRoute(data.user.role));
      } else {
        setError(data.error === "email_taken" ? "Cet email est déjà utilisé." : "Erreur lors de l'inscription.");
      }
    } catch {
      setError("Impossible de contacter le serveur.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-center">
      <div className="card card-md">
        <h2 style={styles.title}>Inscription</h2>
        <p style={styles.subtitle}>Créez votre compte pour accéder à la plateforme.</p>
        {error && <p style={styles.error}>{error}</p>}
        <form onSubmit={handleRegister} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input type="email" placeholder="exemple@email.com" value={email}
              onChange={(e) => setEmail(e.target.value)} style={styles.input} required />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Mot de passe</label>
            <input type="password" placeholder="6 caractères minimum" value={password}
              onChange={(e) => setPassword(e.target.value)} style={styles.input} required minLength={6} />
          </div>
          <div style={styles.field}>
            <label style={styles.label}>Rôle</label>
            <select value={role} onChange={(e) => setRole(e.target.value)} style={styles.input}>
              <option value="operator">Opérateur</option>
              <option value="supplier">Comptable / CRM</option>
              <option value="admin">Conformité</option>
            </select>
          </div>
          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? "Inscription..." : "S'inscrire"}
          </button>
        </form>
        <p style={styles.footerText}>
          Déjà un compte ?{" "}
          <Link to="/login" style={styles.link}>Se connecter</Link>
        </p>
        <Link className="back-link" to="/">← Retour à l'accueil</Link>
      </div>
    </div>
  );
}

const styles = {
  title: { marginBottom: "10px", color: "#0f766e" },
  subtitle: { marginBottom: "24px", color: "#00695c" },
  error: { color: "#c62828", backgroundColor: "#ffcdd2", padding: "0.75rem", borderRadius: "6px", marginBottom: "1rem" },
  form: { display: "flex", flexDirection: "column", gap: "18px" },
  field: { display: "flex", flexDirection: "column", gap: "8px" },
  label: { fontWeight: "600", color: "#0f766e" },
  input: { padding: "12px", border: "1px solid #b2dfdb", borderRadius: "8px", fontSize: "15px" },
  button: { marginTop: "10px", padding: "12px", backgroundColor: "#0f766e", color: "white", border: "none", borderRadius: "8px", fontSize: "16px", fontWeight: "600", cursor: "pointer" },
  footerText: { marginTop: "18px", color: "#00695c" },
  link: { color: "#0f766e", fontWeight: "600", textDecoration: "none" },
};
