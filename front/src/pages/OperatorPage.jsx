import { Link } from "react-router-dom";
import UploadBox from "../components/UploadBox";

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
            <h3>📋 Formats acceptés</h3>
            <ul>
              <li>Factures fournisseurs (PDF, JPG, PNG)</li>
              <li>Taille max : 25 MB par fichier</li>
              <li>Jusqu'à 20 fichiers simultanément</li>
            </ul>
          </div>
          <div style={styles.instructionCard}>
            <h3>⚡ Traitement automatique</h3>
            <ul>
              <li>OCR + extraction des champs clés (SIRET, TVA, montants)</li>
              <li>Vérification de cohérence par IA</li>
              <li>Détection d'anomalies</li>
            </ul>
          </div>
        </div>

        <UploadBox />

        <Link className="back-link" to="/">← Retour à l'accueil</Link>
      </div>
    </div>
  );
}

const styles = {
  header: { marginBottom: "2rem", borderBottom: "2px solid #e0f2f1", paddingBottom: "1.5rem" },
  instructions: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1rem", marginBottom: "1rem" },
  instructionCard: { backgroundColor: "#f0fffe", border: "1px solid #b2dfdb", borderRadius: "8px", padding: "1.5rem" },
};
