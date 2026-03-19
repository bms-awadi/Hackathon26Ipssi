import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { fetchSuppliers, fetchDocuments } from "../api/client";

export default function HomePage() {
  const [stats, setStats] = useState({ suppliers: 0, documents: 0, anomalies: 0, avgConfidence: "—" });
  const isAuthenticated = localStorage.getItem("isAuthenticated") === "true";

  useEffect(() => {
    if (!isAuthenticated) return;
    Promise.all([fetchSuppliers(), fetchDocuments()])
      .then(([suppliers, documents]) => {
        const anomalies = documents.filter((d) => d.anomalies?.length > 0).length;
        const scores = documents
          .map((d) => d.ocrConfidence)
          .filter((s) => s != null);
        const avg = scores.length > 0
        ? `${(scores.reduce((a, b) => a + b, 0) / scores.length * 100).toFixed(0)}%`
        : "—";
        setStats({ suppliers: suppliers.length, documents: documents.length, anomalies, avgConfidence: avg });
      })
      .catch(() => {});
  }, [isAuthenticated]);

  return (
    <div className="page-center">
      <div className="hero-section">
        <div className="hero-content">
          <div style={styles.badge}>Hackathon 2026 · Plateforme CRM & Conformité</div>

          <h1 style={styles.heroTitle}>Plateforme CRM & Conformité</h1>

          <p style={styles.heroText}>
            Centralisez vos dossiers fournisseurs, analysez automatiquement les documents
            avec l'IA et assurez la conformité réglementaire en temps réel.
          </p>

          <div style={styles.quickStats}>
            <div style={styles.quickStat}>
              <span style={styles.quickStatNumber}>{stats.suppliers}</span>
              <span style={styles.quickStatLabel}>Fournisseurs</span>
            </div>
            <div style={styles.quickStat}>
              <span style={styles.quickStatNumber}>{stats.documents}</span>
              <span style={styles.quickStatLabel}>Documents</span>
            </div>
            <div style={styles.quickStat}>
              <span style={styles.quickStatNumber}>{stats.avgConfidence}</span>
              <span style={styles.quickStatLabel}>Confiance IA</span>
            </div>
            <div style={styles.quickStat}>
              <span style={styles.quickStatNumber}>{stats.anomalies}</span>
              <span style={styles.quickStatLabel}>Anomalies</span>
            </div>
          </div>

          {!isAuthenticated && (
            <div style={styles.actions}>
              <Link className="link-button secondary" to="/login">Se connecter</Link>
              <Link className="link-button secondary" to="/register">S'inscrire</Link>
            </div>
          )}
        </div>

        <div className="hero-visual">
          <div style={styles.featureCard}>
            <h3>🔍 Analyse automatique</h3>
            <p>Extraction intelligente des données des documents PDF et factures.</p>
          </div>
          <div style={styles.featureCard}>
            <h3>⚖️ Conformité réglementaire</h3>
            <p>Contrôle en temps réel des anomalies et cohérence des données.</p>
          </div>
          <div style={styles.featureCard}>
            <h3>📈 Tableaux de bord</h3>
            <p>Visualisez l'état de vos dossiers et prenez des décisions éclairées.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  badge: { display: "inline-block", padding: "8px 16px", backgroundColor: "#e0f2f1", color: "#0f766e", borderRadius: "20px", fontSize: "14px", fontWeight: "500", marginBottom: "24px" },
  heroTitle: { fontSize: "48px", lineHeight: "1.2", fontWeight: "700", marginBottom: "16px", color: "#0f766e" },
  heroText: { fontSize: "20px", color: "#00695c", maxWidth: "600px", lineHeight: "1.6", marginBottom: "32px" },
  quickStats: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: "24px", marginBottom: "40px" },
  quickStat: { textAlign: "center" },
  quickStatNumber: { display: "block", fontSize: "32px", fontWeight: "700", color: "#0f766e" },
  quickStatLabel: { fontSize: "14px", color: "#00695c", fontWeight: "500" },
  actions: { display: "flex", gap: "16px", flexWrap: "wrap", marginBottom: "40px" },
  featureCard: { backgroundColor: "#f0fffe", border: "1px solid #b2dfdb", borderRadius: "8px", padding: "1.5rem" },
};
