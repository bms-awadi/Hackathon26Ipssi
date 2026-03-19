export default function ComplianceTable({ documents }) {
  const statusMap = { uploaded: "Uploadé", processing: "En traitement", done: "Traité", error: "Erreur" };

  const getStatusStyle = (status) => {
    if (status === "done") return { backgroundColor: "#c8e6c9", color: "#2e7d32" };
    if (status === "processing") return { backgroundColor: "#fff3e0", color: "#e65100" };
    if (status === "error") return { backgroundColor: "#ffcdd2", color: "#c62828" };
    return { backgroundColor: "#e0f2f1", color: "#00695c" };
  };

  const isExpiringSoon = (date) => {
    if (!date) return false;
    const diff = Math.ceil((new Date(date) - new Date()) / (1000 * 60 * 60 * 24));
    return diff <= 30 && diff > 0;
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return "#2e7d32";
    if (score >= 0.6) return "#e65100";
    return "#c62828";
  };

  return (
    <div style={styles.container}>
      <table style={styles.table}>
        <thead style={styles.thead}>
          <tr>
            <th style={styles.th}>Fichier</th>
            <th style={styles.th}>Type</th>
            <th style={styles.th}>Statut</th>
            <th style={styles.th}>Anomalies</th>
            <th style={styles.th}>Expiration</th>
            <th style={styles.th}>Confiance IA</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => {
            const anomalies = doc.anomalies || [];
            const score = doc.ocrConfidence ?? null;
            const expiration = doc.contract?.date_expiration || null;

            return (
              <tr key={doc.documentId || doc._id} style={styles.tr}>
                <td style={styles.td}>
                  <span style={{ color: "#0f766e", fontWeight: "500" }}>
                    {doc.filename || doc.documentId?.slice(0, 12) || "—"}
                  </span>
                </td>
                <td style={styles.td}>
                  <span style={{ fontWeight: "500", color: "#0f766e", textTransform: "capitalize" }}>
                    {doc.documentType || "—"}
                  </span>
                </td>
                <td style={styles.td}>
                  <span style={{ ...styles.badge, ...getStatusStyle(doc.status) }}>
                    {statusMap[doc.status] || doc.status}
                  </span>
                </td>
                <td style={styles.td}>
                  {anomalies.length > 0 ? (
                    <span style={{ color: "#c62828", fontWeight: "bold" }}>{anomalies.join(", ")}</span>
                  ) : (
                    <span style={{ color: "#2e7d32", fontWeight: "bold" }}>Aucune</span>
                  )}
                </td>
                <td style={styles.td}>
                  {expiration ? (
                    <span style={isExpiringSoon(expiration) ? styles.expiringSoon : styles.normal}>
                      {new Date(expiration).toLocaleDateString("fr-FR")}
                    </span>
                  ) : "—"}
                </td>
                <td style={styles.td}>
                  {score != null ? (
                    <div style={styles.confidenceBar}>
                      <div style={{ ...styles.confidenceFill, width: `${score * 100}%`, backgroundColor: getConfidenceColor(score) }} />
                      <span style={styles.confidenceText}>{(score * 100).toFixed(0)}%</span>
                    </div>
                  ) : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

const styles = {
  container: { overflowX: "auto", marginTop: "1.5rem", borderRadius: "8px", border: "1px solid #b2dfdb" },
  table: { width: "100%", borderCollapse: "collapse", fontSize: "0.95rem" },
  thead: { backgroundColor: "#0f766e", color: "white" },
  th: { padding: "1rem", textAlign: "left", fontWeight: "600", fontSize: "0.9rem", borderBottom: "2px solid #0f766e" },
  tr: { borderBottom: "1px solid #e0f2f1" },
  td: { padding: "1rem", verticalAlign: "middle" },
  badge: { display: "inline-flex", padding: "4px 10px", borderRadius: "999px", fontSize: "12px", fontWeight: "700" },
  expiringSoon: { color: "#e65100", fontWeight: "bold" },
  normal: { color: "#00695c" },
  confidenceBar: { display: "flex", alignItems: "center", gap: "8px" },
  confidenceFill: { height: "8px", borderRadius: "4px", minWidth: "40px" },
  confidenceText: { fontSize: "12px", fontWeight: "500", color: "#00695c" },
};
