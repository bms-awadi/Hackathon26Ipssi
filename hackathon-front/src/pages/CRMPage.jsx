import { Link } from 'react-router-dom';
import { useState } from 'react';
import { suppliers } from '../data/mockData';

export default function CRMPage() {
  const [searchTerm, setSearchTerm] = useState('');

  const statusCounts = suppliers.reduce(
    (acc, supplier) => {
      const hasError = supplier.documents.some((doc) => doc.status === 'Erreur');
      const hasAnomaly = supplier.documents.some((doc) => doc.anomaly !== 'Aucune');

      if (hasError) acc.nonConforme += 1;
      else if (hasAnomaly) acc.aVerifier += 1;
      else acc.conforme += 1;

      return acc;
    },
    { conforme: 0, aVerifier: 0, nonConforme: 0 }
  );

  const totalDossiers = suppliers.length;
  const [filter, setFilter] = useState('Tous');

  const filteredSuppliers = suppliers
    .filter((supplier) => {
      if (filter === 'Conforme') {
        return (
          !supplier.documents.some((doc) => doc.anomaly !== 'Aucune') &&
          !supplier.documents.some((doc) => doc.status === 'Erreur')
        );
      }
      if (filter === 'À vérifier') {
        return (
          !supplier.documents.some((doc) => doc.status === 'Erreur') &&
          supplier.documents.some((doc) => doc.anomaly !== 'Aucune')
        );
      }
      if (filter === 'Non conforme') {
        return supplier.documents.some((doc) => doc.status === 'Erreur');
      }
      return true;
    })
    .filter((supplier) =>
      supplier.companyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      supplier.siret.includes(searchTerm)
    );

  return (
    <div className="page">
      <div className="card card-lg">
        <div style={styles.header}>
          <h2>🗂️ CRM documentaire</h2>
          <p>
            Consultez et gérez vos dossiers fournisseurs, suivez l'état de
            conformité des documents et accédez rapidement aux modules d'analyse.
          </p>
        </div>

        <div style={styles.statsRow}>
          <div style={styles.statCard}>
            <div style={styles.statIcon}>📁</div>
            <div style={styles.statContent}>
              <p style={styles.statLabel}>Dossiers totaux</p>
              <p style={styles.statValue}>{totalDossiers}</p>
            </div>
          </div>

          <div style={styles.statCard}>
            <div style={styles.statIcon}>✅</div>
            <div style={styles.statContent}>
              <p style={styles.statLabel}>Conformes</p>
              <p style={styles.statValue}>{statusCounts.conforme}</p>
            </div>
          </div>

          <div style={styles.statCard}>
            <div style={styles.statIcon}>⚠️</div>
            <div style={styles.statContent}>
              <p style={styles.statLabel}>À vérifier</p>
              <p style={styles.statValue}>{statusCounts.aVerifier}</p>
            </div>
          </div>

          <div style={styles.statCard}>
            <div style={styles.statIcon}>❌</div>
            <div style={styles.statContent}>
              <p style={styles.statLabel}>Non conformes</p>
              <p style={styles.statValue}>{statusCounts.nonConforme}</p>
            </div>
          </div>
        </div>

        <div style={styles.controlsSection}>
          <input
            type="text"
            placeholder="🔍 Rechercher une entreprise, SIRET..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={styles.searchInput}
          />

          <div style={styles.filterButtons}>
            {['Tous', 'Conforme', 'À vérifier', 'Non conforme'].map((label) => (
              <button
                key={label}
                type="button"
                onClick={() => setFilter(label)}
                style={
                  filter === label
                    ? styles.filterButtonActive
                    : styles.filterButton
                }
              >
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
              {filteredSuppliers.map((supplier) => {
                const anomaliesCount = supplier.documents.filter(
                  (doc) => doc.anomaly !== 'Aucune'
                ).length;

                const hasError = supplier.documents.some(
                  (doc) => doc.status === 'Erreur'
                );

                const globalStatus = hasError
                  ? 'Non conforme'
                  : anomaliesCount > 0
                  ? 'À vérifier'
                  : 'Conforme';

                return (
                  <tr key={supplier.supplier_id} style={styles.tr}>
                    <td style={styles.td}>
                      <div style={styles.companyName}>{supplier.companyName}</div>
                      <div style={styles.companySub}>{supplier.contact}</div>
                    </td>

                    <td style={styles.td}>{supplier.siret}</td>

                    <td style={styles.td}>
                      <span style={styles.docCount}>
                        {supplier.documents.length}
                      </span>
                    </td>

                    <td style={styles.td}>
                      <span
                        style={
                          globalStatus === 'Conforme'
                            ? styles.badgeGood
                            : globalStatus === 'À vérifier'
                            ? styles.badgeWarning
                            : styles.badgeError
                        }
                      >
                        {globalStatus}
                      </span>
                    </td>

                    <td style={styles.td}>
                      <Link
                        to={`/crm/${supplier.supplier_id}`}
                        style={styles.actionLink}
                      >
                        Détail
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filteredSuppliers.length === 0 && (
          <div style={styles.emptyState}>
            <p>Aucun dossier ne correspond à votre recherche</p>
          </div>
        )}

        <Link className="back-link" to="/">
          ← Retour à l'accueil
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
  statsRow: {
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
    cursor: 'default',
  },
  statIcon: {
    fontSize: '2rem',
    lineHeight: '1',
  },
  statContent: {
    flex: 1,
  },
  statLabel: {
    fontSize: '0.875rem',
    color: '#00695c',
    fontWeight: '500',
    margin: '0 0 0.25rem 0',
  },
  statValue: {
    fontSize: '1.75rem',
    fontWeight: '700',
    color: '#0f766e',
    margin: '0',
    lineHeight: '1',
  },
  controlsSection: {
    marginBottom: '2rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
  },
  searchInput: {
    padding: '0.75rem 1rem',
    fontSize: '0.95rem',
    border: '2px solid #b2dfdb',
    borderRadius: '6px',
    width: '100%',
    boxSizing: 'border-box',
    transition: 'border-color 0.3s ease',
    fontFamily: 'inherit',
  },
  filterButtons: {
    display: 'flex',
    gap: '0.5rem',
    flexWrap: 'wrap',
  },
  filterButton: {
    padding: '0.6rem 1rem',
    backgroundColor: '#f0fffe',
    border: '1px solid #b2dfdb',
    color: '#00695c',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.9rem',
    fontWeight: '500',
    transition: 'all 0.3s ease',
  },
  filterButtonActive: {
    padding: '0.6rem 1rem',
    backgroundColor: '#0f766e',
    border: '1px solid #0f766e',
    color: 'white',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.9rem',
    fontWeight: '500',
    transition: 'all 0.3s ease',
  },
  tableContainer: {
    overflowX: 'auto',
    marginBottom: '1.5rem',
    borderRadius: '8px',
    border: '1px solid #b2dfdb',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '0.95rem',
  },
  thead: {
    backgroundColor: '#0f766e',
    color: 'white',
  },
  th: {
    padding: '1rem',
    textAlign: 'left',
    fontWeight: '600',
    fontSize: '0.9rem',
    letterSpacing: '0.5px',
    borderBottom: '2px solid #0f766e',
  },
  tr: {
    borderBottom: '1px solid #e0f2f1',
    transition: 'background-color 0.2s ease',
  },
  td: {
    padding: '1rem',
    verticalAlign: 'middle',
  },
  companyName: {
    fontWeight: '600',
    color: '#0f766e',
    fontSize: '0.95rem',
  },
  companySub: {
    fontSize: '0.8rem',
    color: '#80cbc4',
    marginTop: '0.25rem',
  },
  docCount: {
    display: 'inline-block',
    padding: '0.25rem 0.75rem',
    backgroundColor: '#e0f2f1',
    color: '#00695c',
    borderRadius: '4px',
    fontSize: '0.85rem',
    fontWeight: '600',
  },
  badgeGood: {
    display: 'inline-block',
    padding: '0.4rem 0.8rem',
    backgroundColor: '#c8e6c9',
    color: '#2e7d32',
    borderRadius: '4px',
    fontSize: '0.85rem',
    fontWeight: '600',
    whiteSpace: 'nowrap',
  },
  badgeWarning: {
    display: 'inline-block',
    padding: '0.4rem 0.8rem',
    backgroundColor: '#fff3e0',
    color: '#e65100',
    borderRadius: '4px',
    fontSize: '0.85rem',
    fontWeight: '600',
    whiteSpace: 'nowrap',
  },
  badgeError: {
    display: 'inline-block',
    padding: '0.4rem 0.8rem',
    backgroundColor: '#ffcdd2',
    color: '#c62828',
    borderRadius: '4px',
    fontSize: '0.85rem',
    fontWeight: '600',
    whiteSpace: 'nowrap',
  },
  actionLink: {
    color: '#0f766e',
    textDecoration: 'none',
    fontWeight: '500',
    transition: 'color 0.2s ease',
    cursor: 'pointer',
  },
  emptyState: {
    padding: '2rem',
    textAlign: 'center',
    color: '#80cbc4',
    fontSize: '1rem',
    marginBottom: '1rem',
  },
};