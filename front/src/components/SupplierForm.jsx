export default function SupplierForm({ supplier }) {
  return (
    <div style={styles.card}>
      <h3 style={styles.title}>Fiche fournisseur</h3>

      <div style={styles.row}>
        <span style={styles.label}>Raison sociale :</span>
        <span>{supplier.companyName || 'Non disponible'}</span>
      </div>

      <div style={styles.row}>
        <span style={styles.label}>SIRET :</span>
        <span>{supplier.siret || 'Non disponible'}</span>
      </div>

      <div style={styles.row}>
        <span style={styles.label}>RIB :</span>
        <span>{supplier.rib || 'Non disponible'}</span>
      </div>

      <div style={styles.row}>
        <span style={styles.label}>Contact :</span>
        <span>{supplier.contact || 'Non disponible'}</span>
      </div>
    </div>
  );
}

const styles = {
  card: {
    border: '1px solid #ddd',
    borderRadius: '10px',
    padding: '20px',
    marginTop: '20px',
    backgroundColor: '#f9fafb',
  },
  title: {
    marginBottom: '20px',
  },
  row: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '10px 0',
    borderBottom: '1px solid #eee',
  },
  label: {
    fontWeight: 'bold',
  },
};