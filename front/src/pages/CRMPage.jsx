import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { fetchSuppliers } from "../api/client";

export default function CRMPage() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filter, setFilter] = useState("Tous");

  useEffect(() => {
    fetchSuppliers()
      .then(setSuppliers)
      .catch(() => setSuppliers([]))
      .finally(() => setLoading(false));
  }, []);

  const getStatus = (supplier) => {
    const docs = supplier.documents || [];
    if (docs.some((d) => d.status === "error")) return "Non conforme";
    if (docs.some((d) => d.anomalies?.length > 0)) return "À vérifier";
    return "Conforme";
  };

  const counts = suppliers.reduce(
    (acc, s) => {
      const st = getStatus(s);
      if (st === "Non conforme") acc.nonConforme++;
      else if (st === "À vérifier") acc.aVerifier++;
      else acc.conforme++;
      return acc;
    },
    { conforme: 0, aVerifier: 0, nonConforme: 0 }
  );

  const filtered = suppliers
    .filter((s) => filter === "Tous" || getStatus(s) === filter)
    .filter((s) =>
      (s.companyName || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.siret || "").includes(searchTerm)
    );

  if (loading) return <div className="page"><div className="card card-lg"><p>Chargement des fournisseurs...</p></div></div>;

  return (
    <div className="page">
      <div className="card card-lg">
        <div style={styles.header}>
          <h2>🗂️ CRM documentaire</h2>
          <p>Consultez et gérez vos dossiers fournisseurs, suivez l'état de conformité des documents.</p>
        </div>

        <div style={styles.statsRow}>
          {[
            { icon: "📁", label: "Dossiers totaux", value: suppliers.length },
            { icon: "✅", label: "Conformes", value: counts.conforme },
            { icon: "⚠️", label: "À vérifier", value: counts.aVerifier },
            { icon: "❌", label: "Non conformes", value: counts.nonConforme },
          ].map((s) => (
            <div key={s.label} style={styles.statCard}>
              <div style={styles.statIcon}>{s.icon}</div>
              <div style={styles.statContent}>
                <p style={styles.statLabel}>{s.label}</p>
                <p style={styles.statValue}>{s.value}</p>
              </div>
            </div>
          ))}
        </div>

        <div style={styles.controlsSection}>
          <input type="text" placeholder="🔍 Rechercher une entreprise, SIRET..."
            value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} style={styles.searchInput} />
          <div style={styles.filterButtons}>
            {["Tous", "Conforme", "À vérifier", "Non conforme"].map((label) => (
              <button key={label} type="button" onClick={() => setFilter(label)}
                style={filter === label ? styles.filterButtonActive : styles.filterButton}>
                {label}
              </button>
            ))}
          </div>
        </div>

        <div style={styles.tableContainer}>
          <table style={styles.table}>
            <thead style={styles.thead}>
              <tr>
                <th style={styles.th}>Entreprise</th>
                <th style={styles.th}>SIRET</th>
                <th style={styles.th}>Documents</th>
                <th style={styles.th}>Statut</th>
                <th style={styles.th}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((supplier) => {
                const status = getStatus(supplier);
                return (
                  <tr key={supplier._id} style={styles.tr}>
                    <td style={styles.td}>
                      <div style={styles.companyName}>{supplier.companyName}</div>
                      <div style={styles.companySub}>{supplier.contactEmail}</div>
                    </td>
                    <td style={styles.td}>{supplier.siret || "—"}</td>
                    <td style={styles.td}>
                      <span style={styles.docCount}>{supplier.documents.length || 0}</span>
                    </td>
                    <td style={styles.td}>
                      <span style={status === "Conforme" ? styles.badgeGood : status === "À vérifier" ? styles.badgeWarning : styles.badgeError}>
                        {status}
                      </span>
                    </td>
                    <td style={styles.td}>
                      <Link to={`/crm/${supplier._id}`} style={styles.actionLink}>Détail</Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filtered.length === 0 && (
          <div style={styles.emptyState}>
            <p>{suppliers.length === 0 ? "Aucun fournisseur enregistré pour le moment." : "Aucun résultat pour cette recherche."}</p>
          </div>
        )}

        <Link className="back-link" to="/">← Retour à l'accueil</Link>
      </div>
    </div>
  );
}

const styles = {
  header: { marginBottom: "2rem", borderBottom: "2px solid #e0f2f1", paddingBottom: "1.5rem" },
  statsRow: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" },
  statCard: { display: "flex", alignItems: "center", gap: "1rem", padding: "1.2rem", backgroundColor: "#f0fffe", border: "1px solid #b2dfdb", borderRadius: "8px" },
  statIcon: { fontSize: "2rem", lineHeight: "1" },
  statContent: { flex: 1 },
  statLabel: { fontSize: "0.875rem", color: "#00695c", fontWeight: "500", margin: "0 0 0.25rem 0" },
  statValue: { fontSize: "1.75rem", fontWeight: "700", color: "#0f766e", margin: "0", lineHeight: "1" },
  controlsSection: { marginBottom: "2rem", display: "flex", flexDirection: "column", gap: "1rem" },
  searchInput: { padding: "0.75rem 1rem", fontSize: "0.95rem", border: "2px solid #b2dfdb", borderRadius: "6px", width: "100%", boxSizing: "border-box" },
  filterButtons: { display: "flex", gap: "0.5rem", flexWrap: "wrap" },
  filterButton: { padding: "0.6rem 1rem", backgroundColor: "#f0fffe", border: "1px solid #b2dfdb", color: "#00695c", borderRadius: "6px", cursor: "pointer", fontSize: "0.9rem", fontWeight: "500" },
  filterButtonActive: { padding: "0.6rem 1rem", backgroundColor: "#0f766e", border: "1px solid #0f766e", color: "white", borderRadius: "6px", cursor: "pointer", fontSize: "0.9rem", fontWeight: "500" },
  tableContainer: { overflowX: "auto", marginBottom: "1.5rem", borderRadius: "8px", border: "1px solid #b2dfdb" },
  table: { width: "100%", borderCollapse: "collapse", fontSize: "0.95rem" },
  thead: { backgroundColor: "#0f766e", color: "white" },
  th: { padding: "1rem", textAlign: "left", fontWeight: "600", fontSize: "0.9rem" },
  tr: { borderBottom: "1px solid #e0f2f1" },
  td: { padding: "1rem", verticalAlign: "middle" },
  companyName: { fontWeight: "600", color: "#0f766e", fontSize: "0.95rem" },
  companySub: { fontSize: "0.8rem", color: "#80cbc4", marginTop: "0.25rem" },
  docCount: { display: "inline-block", padding: "0.25rem 0.75rem", backgroundColor: "#e0f2f1", color: "#00695c", borderRadius: "4px", fontSize: "0.85rem", fontWeight: "600" },
  badgeGood: { display: "inline-block", padding: "0.4rem 0.8rem", backgroundColor: "#c8e6c9", color: "#2e7d32", borderRadius: "4px", fontSize: "0.85rem", fontWeight: "600" },
  badgeWarning: { display: "inline-block", padding: "0.4rem 0.8rem", backgroundColor: "#fff3e0", color: "#e65100", borderRadius: "4px", fontSize: "0.85rem", fontWeight: "600" },
  badgeError: { display: "inline-block", padding: "0.4rem 0.8rem", backgroundColor: "#ffcdd2", color: "#c62828", borderRadius: "4px", fontSize: "0.85rem", fontWeight: "600" },
  actionLink: { color: "#0f766e", textDecoration: "none", fontWeight: "500" },
  emptyState: { padding: "2rem", textAlign: "center", color: "#80cbc4" },
};
