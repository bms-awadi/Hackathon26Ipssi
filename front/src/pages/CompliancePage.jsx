import { Link } from 'react-router-dom';
import ComplianceTable from '../components/ComplianceTable';
import { documents } from '../data/mockData';

export default function CompliancePage() {
  const totalDocuments = documents.length;
  const anomaliesCount = documents.filter((doc) => doc.anomaly !== 'Aucune').length;
  const errorsCount = documents.filter((doc) => doc.status === 'Erreur').length;
  const treatedCount = documents.filter((doc) => doc.status === 'Traité').length;

  return (
    <div className="page">
      <div className="card card-lg">
        <div style={styles.header}>
          <h2>📋 Centre de conformité</h2>
          <p>Surveillez l'état de tous vos documents, détectez les anomalies et assurez la conformité réglementaire.</p>
        </div>

        <div style={styles.statsGrid}>
          <div style={styles.statCard}>
            <div style={styles.statIcon}>📄</div>
            <div style={styles.statContent}>
              <div style={styles.statNumber}>{totalDocuments}</div>
              <div style={styles.statLabel}>Documents totaux</div>
            </div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statIcon}>✅</div>
            <div style={styles.statContent}>
              <div style={styles.statNumber}>{treatedCount}</div>
              <div style={styles.statLabel}>Traités</div>
            </div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statIcon}>⚠️</div>
            <div style={styles.statContent}>
              <div style={styles.statNumber}>{anomaliesCount}</div>
              <div style={styles.statLabel}>Anomalies</div>
            </div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statIcon}>❌</div>
            <div style={styles.statContent}>
              <div style={styles.statNumber}>{errorsCount}</div>
              <div style={styles.statLabel}>Erreurs</div>
            </div>
          </div>
        </div>

        <div style={styles.tableSection}>
          <h3>Détail des documents</h3>
          <ComplianceTable documents={documents} />
        </div>

        <Link className="back-link" to="/">
          Retour à l'accueil
        </Link>
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
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1rem',
    marginBottom: '2rem',
  },
  statCard: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    padding: '1.2rem',
    backgroundColor: '#f0fffe',
    border: '1px solid #b2dfdb',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(15, 118, 110, 0.08)',
    transition: 'all 0.3s ease',
  },
  statIcon: {
    fontSize: '2rem',
    lineHeight: '1',
  },
  statContent: {
    flex: 1,
  },
  statNumber: {
    fontSize: '1.75rem',
    fontWeight: '700',
    color: '#0f766e',
    margin: '0',
    lineHeight: '1',
  },
  statLabel: {
    fontSize: '0.875rem',
    color: '#00695c',
    fontWeight: '500',
    margin: '0.25rem 0 0 0',
  },
  tableSection: {
    marginTop: '2rem',
  },
};