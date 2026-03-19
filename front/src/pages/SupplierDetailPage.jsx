import { Link, useParams } from 'react-router-dom';
import { suppliers } from '../data/mockData';

export default function SupplierDetailPage() {
  const { supplierId } = useParams();

  const supplier = suppliers.find((item) => item.supplier_id === supplierId);

  if (!supplier) {
    return (
      <div className="page">
        <div className="card card-md">
          <h2>Fournisseur introuvable</h2>
          <Link className="back-link" to="/crm">
            Retour au CRM
          </Link>
        </div>
      </div>
    );
  }

  const anomaliesCount = supplier.documents.filter(
    (doc) => doc.anomaly !== 'Aucune'
  ).length;

  const globalStatus = anomaliesCount > 0 ? 'À vérifier' : 'Conforme';

  const getStatusStyle = (status) => {
    if (status === 'Traité') return { color: '#10b981', fontWeight: 'bold' };
    if (status === 'En traitement') return { color: '#f59e0b', fontWeight: 'bold' };
    if (status === 'Erreur') return { color: '#ef4444', fontWeight: 'bold' };
    return { color: '#6b7280' };
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
          <p><strong>SIRET :</strong> {supplier.siret}</p>
          <p><strong>RIB :</strong> {supplier.rib}</p>
          <p><strong>Contact :</strong> {supplier.contact}</p>
          <p><strong>Statut global :</strong> <span style={globalStatus === 'Conforme' ? styles.statusGood : styles.statusBad}>{globalStatus}</span></p>
        </div>

        <div style={styles.documentsSection}>
          <h3>Documents du dossier</h3>

          <div style={styles.documentsGrid}>
            {supplier.documents.map((doc) => (
              <div key={doc.document_id} style={styles.docCard}>
                <p><strong>ID :</strong> {doc.document_id}</p>
                <p><strong>Type :</strong> {doc.document_type}</p>
                <p><strong>Statut :</strong> <span style={getStatusStyle(doc.status)}>{doc.status}</span></p>
                <p><strong>Anomalie :</strong> <span style={doc.anomaly === 'Aucune' ? styles.statusGood : styles.statusBad}>{doc.anomaly}</span></p>
                <p><strong>Expiration :</strong> {doc.date_expiration || '—'}</p>
                <p><strong>Confiance :</strong> {doc.confidence_score}</p>
              </div>
            ))}
          </div>
        </div>

        <Link className="back-link" to="/crm">
          Retour au CRM
        </Link>
        <br />
    
      </div>
    </div>
  );
}

const styles = {
  header: {
    marginBottom: '2rem',
    borderBottom: '2px solid #e0f2f1',
    paddingBottom: '1.5rem',
  },
  supplierInfo: {
    backgroundColor: '#f0fffe',
    padding: '1.5rem',
    borderRadius: '8px',
    marginBottom: '1.5rem',
    border: '1px solid #b2dfdb',
  },
  documentsSection: {
    marginTop: '2rem',
  },
  documentsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: '1rem',
    marginTop: '1rem',
  },
  docCard: {
    backgroundColor: '#fff',
    border: '1px solid #b2dfdb',
    borderRadius: '8px',
    padding: '1rem',
    boxShadow: '0 2px 4px rgba(15, 118, 110, 0.08)',
  },
  statusGood: {
    color: '#2e7d32',
    fontWeight: 'bold',
  },
  statusBad: {
    color: '#c62828',
    fontWeight: 'bold',
  },
};