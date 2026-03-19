import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { fetchDocuments } from "../api/client";
import ComplianceTable from "../components/ComplianceTable";

export default function CompliancePage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDocuments()
      .then(setDocuments)
      .catch(() => setDocuments([]))
      .finally(() => setLoading(false));
  }, []);

  const totalDocuments = documents.length;
  const anomaliesCount = documents.filter((d) => d.anomalies?.length > 0).length;
  const errorsCount = documents.filter((d) => d.status === "error").length;
  const treatedCount = documents.filter((d) => d.status === "done").length;

  if (loading) return <div className="page"><div className="card card-lg"><p>Chargement...</p></div></div>;

  return (
    <div className="page">
      <div className="card card-lg">
        <div style={styles.header}>
          <h2>📋 Centre de conformité</h2>
          <p>Surveillez l'état de tous vos documents, détectez les anomalies et assurez la conformité réglementaire.</p>
        </div>

        <div style={styles.statsGrid}>
          {[
            { icon: "📄", label: "Documents totaux", value: totalDocuments },
            { icon: "✅", label: "Traités", value: treatedCount },
            { icon: "⚠️", label: "Anomalies", value: anomaliesCount },
            { icon: "❌", label: "Erreurs", value: errorsCount },
          ].map((s) => (
            <div key={s.label} style={styles.statCard}>
              <div style={styles.statIcon}>{s.icon}</div>
              <div style={styles.statContent}>
                <div style={styles.statNumber}>{s.value}</div>
                <div style={styles.statLabel}>{s.label}</div>
              </div>
            </div>
          ))}
        </div>

        <div style={styles.tableSection}>
          <h3>Détail des documents</h3>
          {documents.length === 0 ? (
            <p style={{ color: "#80cbc4", textAlign: "center", padding: "2rem" }}>
              Aucun document traité pour le moment.
            </p>
          ) : (
            <ComplianceTable documents={documents} />
          )}
        </div>

        <Link className="back-link" to="/">← Retour à l'accueil</Link>
      </div>
    </div>
  );
}

const styles = {
  header: { marginBottom: "2rem", borderBottom: "2px solid #e0f2f1", paddingBottom: "1.5rem" },
  statsGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" },
  statCard: { display: "flex", alignItems: "center", gap: "1rem", padding: "1.2rem", backgroundColor: "#f0fffe", border: "1px solid #b2dfdb", borderRadius: "8px" },
  statIcon: { fontSize: "2rem", lineHeight: "1" },
  statContent: { flex: 1 },
  statNumber: { fontSize: "1.75rem", fontWeight: "700", color: "#0f766e", lineHeight: "1" },
  statLabel: { fontSize: "0.875rem", color: "#00695c", fontWeight: "500", marginTop: "0.25rem" },
  tableSection: { marginTop: "2rem" },
};
