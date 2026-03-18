import { Link } from 'react-router-dom';
import UploadBox from '../components/UploadBox';

export default function OperatorPage() {
  return (
    <div className="page">
      <div className="card card-lg">
        <div style={styles.header}>
          <h2>📤 Espace opérateur</h2>
          <p>Importez vos documents pour analyse automatique et intégration dans la plateforme.</p>
        </div>

        <div style={styles.instructions}>
          <div style={styles.instructionCard}>
            <h3>📋 Types de documents acceptés</h3>
            <ul>
              <li>Factures (PDF, JPG)</li>
              <li>RIB (relevés d'identité bancaire)</li>
              <li>KBIS (extraits Kbis)</li>
              <li>Attestations URSSAF</li>
              <li>Autres documents justificatifs</li>
            </ul>
          </div>
          <div style={styles.instructionCard}>
            <h3>⚡ Traitement automatique</h3>
            <p>Une fois importés, vos documents sont :</p>
            <ul>
              <li>Analysés par IA pour extraction des données</li>
              <li>Vérifiés pour conformité réglementaire</li>
              <li>Intégrés dans les dossiers fournisseurs</li>
            </ul>
          </div>
        </div>

        <UploadBox />

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
  instructions: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '1rem',
    marginBottom: '2rem',
  },
  instructionCard: {
    backgroundColor: '#f0fffe',
    border: '1px solid #b2dfdb',
    borderRadius: '8px',
    padding: '1.5rem',
    boxShadow: '0 2px 4px rgba(15, 118, 110, 0.08)',
  },
};