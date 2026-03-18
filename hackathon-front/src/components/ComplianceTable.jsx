export default function ComplianceTable({ documents }) {
  const getStatusStyle = (status) => {
    if (status === 'Traité') {
      return { backgroundColor: '#c8e6c9', color: '#2e7d32' };
    }
    if (status === 'En traitement') {
      return { backgroundColor: '#fff3e0', color: '#e65100' };
    }
    if (status === 'Erreur') {
      return { backgroundColor: '#ffcdd2', color: '#c62828' };
    }
    return { backgroundColor: '#e0f2f1', color: '#00695c' };
  };

  const getAnomalyStyle = (anomaly) => {
    if (anomaly === 'Aucune') {
      return { color: '#2e7d32', fontWeight: 'bold' };
    }
    return { color: '#c62828', fontWeight: 'bold' };
  };

  const getTypeStyle = (type) => {
    return { fontWeight: '500', textTransform: 'capitalize', color: '#0f766e' };
  };

  const isExpiringSoon = (date) => {
    if (!date) return false;
    const expirationDate = new Date(date);
    const now = new Date();
    const diffTime = expirationDate - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 30 && diffDays > 0;
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return '#2e7d32';
    if (score >= 0.6) return '#e65100';
    return '#c62828';
  };

  return (
    <div style={styles.container}>
      <table style={styles.table}>
        <thead style={styles.thead}>
          <tr>
            <th style={styles.th}>ID Document</th>
            <th style={styles.th}>Type</th>
            <th style={styles.th}>Statut</th>
            <th style={styles.th}>Anomalie</th>
            <th style={styles.th}>Expiration</th>
            <th style={styles.th}>Confiance IA</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.document_id} style={styles.tr}>
              <td style={styles.td}>{doc.document_id}</td>
              <td style={styles.td}>
                <span style={getTypeStyle(doc.document_type)}>{doc.document_type}</span>
              </td>
              <td style={styles.td}>
                <span style={{ ...styles.badge, ...getStatusStyle(doc.status) }}>
                  {doc.status}
                </span>
              </td>
              <td style={styles.td}>
                <span style={getAnomalyStyle(doc.anomaly)}>
                  {doc.anomaly}
                </span>
              </td>
              <td style={styles.td}>
                {doc.date_expiration ? (
                  <span style={isExpiringSoon(doc.date_expiration) ? styles.expiringSoon : styles.normal}>
                    {doc.date_expiration}
                  </span>
                ) : (
                  '—'
                )}
              </td>
              <td style={styles.td}>
                <div style={styles.confidenceBar}>
                  <div
                    style={{
                      ...styles.confidenceFill,
                      width: `${doc.confidence_score * 100}%`,
                      backgroundColor: getConfidenceColor(doc.confidence_score),
                    }}
                  />
                  <span style={styles.confidenceText}>{(doc.confidence_score * 100).toFixed(0)}%</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const styles = {
  container: {
    overflowX: 'auto',
    marginTop: '1.5rem',
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
  badge: {
    display: 'inline-flex',
    padding: '4px 10px',
    borderRadius: '999px',
    fontSize: '12px',
    fontWeight: '700',
  },
  expiringSoon: {
    color: '#e65100',
    fontWeight: 'bold',
  },
  normal: {
    color: '#00695c',
  },
  confidenceBar: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  confidenceFill: {
    height: '8px',
    borderRadius: '4px',
    minWidth: '40px',
  },
  confidenceText: {
    fontSize: '12px',
    fontWeight: '500',
    color: '#00695c',
  },
};