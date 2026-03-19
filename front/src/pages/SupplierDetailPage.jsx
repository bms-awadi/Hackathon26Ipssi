import { Link, useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { fetchSupplier } from "../api/client";

export default function SupplierDetailPage() {
  const { supplierId } = useParams();
  const [supplier, setSupplier] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    fetchSupplier(supplierId)
      .then((data) => {
        if (data.error) { setNotFound(true); return; }
        setSupplier(data.supplier);
        setDocuments(data.documents || []);
      })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [supplierId]);

  if (loading) return <div className="page"><div className="card card-lg"><p>Chargement...</p></div></div>;
  if (notFound || !supplier) {
    return (
      <div className="page"><div className="card card-md">
        <h2>Fournisseur introuvable</h2>
        <Link className="back-link" to="/crm">← Retour au CRM</Link>
      </div></div>
    );
  }

  const anomaliesCount = documents.filter((d) => d.anomalies?.length > 0).length;
  const globalStatus = anomaliesCount > 0 ? "À vérifier" : "Conforme";

  const statusMap = { uploaded: "Uploadé", processing: "En traitement", done: "Traité", error: "Erreur" };
  const getStatusStyle = (s) => {
    if (s === "done") return { color: "#2e7d32", fontWeight: "bold" };
    if (s === "processing") return { color: "#e65100", fontWeight: "bold" };
    if (s === "error") return { color: "#c62828", fontWeight: "bold" };
    return { color: "#666" };
  };

  return (
    <div className="page">
      <div className="card card-lg">
        <div style={styles.header}>
          <h2>🏢 Dossier fournisseur</h2>
          <p>Détails complets du fournisseur et état de ses documents.</p>
        </div>

        <div style={styles.supplierInfo}>
          <h3>{supplier.companyName}</h3>
          <p><strong>SIRET :</strong> {supplier.siret || "—"}</p>
          <p><strong>RIB :</strong> {supplier.rib || "—"}</p>
          <p><strong>Contact :</strong> {supplier.contactEmail || "—"}</p>
          <p>
            <strong>Statut global :</strong>{" "}
            <span style={globalStatus === "Conforme" ? styles.statusGood : styles.statusBad}>
              {globalStatus}
            </span>
          </p>
        </div>

        <div style={styles.documentsSection}>
          <h3>Documents du dossier ({documents.length})</h3>
          {documents.length === 0 ? (
            <p style={{ color: "#80cbc4" }}>Aucun document associé à ce fournisseur.</p>
          ) : (
            <div style={styles.documentsGrid}>
              {documents.map((doc) => (
                <div key={doc.documentId} style={styles.docCard}>
                  <p><strong>Fichier :</strong> {doc.filename || doc.documentId?.slice(0, 12)}</p>
                  <p><strong>Type :</strong> {doc.mimeType || doc.filename.split('.').pop() || "—"}</p>
                  <p><strong>Statut :</strong>{" "}
                    <span style={getStatusStyle(doc.status)}>{statusMap[doc.status] || doc.status}</span>
                  </p>
                  <p><strong>Anomalies :</strong>{" "}
                    {doc.anomalies?.length > 0
                      ? <span style={styles.statusBad}>{doc.anomalies.join(", ")}</span>
                      : <span style={styles.statusGood}>Aucune</span>}
                  </p>
                  {doc.contract && (
                    <>
                      <p><strong>SIRET extrait :</strong> {doc.contract.siret || "—"}</p>
                      <p><strong>Montant TTC :</strong> {doc.contract.montant_ttc != null ? `${doc.contract.montant_ttc} €` : "—"}</p>
                      <p><strong>TVA :</strong> {doc.contract.montant_tva != null ? `${doc.contract.montant_tva} €` : "—"}</p>
                      <p><strong>Confiance :</strong> {doc.ocrConfidence != null ? `${(doc.ocrConfidence * 100).toFixed(0)} %` : "—"}</p>
                    </>
                  )}
                  <p style={{ fontSize: "0.8rem", color: "#80cbc4", marginTop: "0.5rem" }}>
                    {doc.createdAt ? new Date(doc.createdAt).toLocaleDateString("fr-FR") : ""}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        <Link className="back-link" to="/crm">← Retour au CRM</Link>
      </div>
    </div>
  );
}

const styles = {
  header: { marginBottom: "2rem", borderBottom: "2px solid #e0f2f1", paddingBottom: "1.5rem" },
  supplierInfo: { backgroundColor: "#f0fffe", padding: "1.5rem", borderRadius: "8px", marginBottom: "1.5rem", border: "1px solid #b2dfdb" },
  documentsSection: { marginTop: "2rem" },
  documentsGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem", marginTop: "1rem" },
  docCard: { backgroundColor: "#fff", border: "1px solid #b2dfdb", borderRadius: "8px", padding: "1rem" },
  statusGood: { color: "#2e7d32", fontWeight: "bold" },
  statusBad: { color: "#c62828", fontWeight: "bold" },
};
