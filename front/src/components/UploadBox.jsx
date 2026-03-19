import { useState } from "react";
import { uploadDocuments } from "../api/client";

export default function UploadBox() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (event) => {
    const newFiles = Array.from(event.target.files);
    setSelectedFiles((prev) => {
      const existing = new Set(prev.map((f) => f.name));
      return [...prev, ...newFiles.filter((f) => !existing.has(f.name))];
    });
    setStatus("");
    setError("");
    event.target.value = "";
  };

  const handleRemoveFile = (fileName) => {
    setSelectedFiles((prev) => prev.filter((f) => f.name !== fileName));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError("Aucun fichier sélectionné.");
      return;
    }
    setUploading(true);
    setError("");
    setStatus("");
    try {
      const data = await uploadDocuments(selectedFiles);
      if (data.documents) {
        setStatus(`✅ ${data.documents.length} document(s) envoyé(s) avec succès. Le pipeline IA va les traiter.`);
        setSelectedFiles([]);
      } else {
        setError("Erreur lors de l'envoi. Vérifiez votre connexion.");
      }
    } catch {
      setError("Impossible de contacter le serveur.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.uploadArea}>
        <div style={styles.uploadIcon}>📎</div>
        <h3>Sélectionnez vos documents</h3>
        <p>PDF, JPG, PNG — max 25 MB par fichier</p>
        <input type="file" multiple accept=".pdf,.jpg,.jpeg,.png,.tiff,.txt"
          onChange={handleFileChange} style={styles.input} />
        <button onClick={handleUpload} style={styles.button} disabled={uploading}>
          {uploading ? "Envoi en cours..." : "Envoyer les documents"}
        </button>
      </div>

      {selectedFiles.length > 0 && (
        <div style={styles.fileList}>
          <h4>Fichiers sélectionnés ({selectedFiles.length})</h4>
          <div style={styles.fileGrid}>
            {selectedFiles.map((file, i) => (
              <div key={i} style={styles.fileItem}>
                <span style={styles.fileName}>{file.name}</span>
                <button onClick={() => handleRemoveFile(file.name)} style={styles.deleteButton}>✕</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && <div style={styles.errorStatus}>{error}</div>}
      {status && <div style={styles.successStatus}>{status}</div>}
    </div>
  );
}

const styles = {
  container: { marginTop: "32px" },
  uploadArea: { border: "2px dashed #b2dfdb", borderRadius: "12px", padding: "40px", textAlign: "center", backgroundColor: "#f0fffe", marginBottom: "24px" },
  uploadIcon: { fontSize: "48px", marginBottom: "16px" },
  input: { display: "block", margin: "20px auto" },
  button: { padding: "12px 24px", border: "none", borderRadius: "8px", backgroundColor: "#0f766e", color: "white", cursor: "pointer", fontSize: "16px", fontWeight: "600" },
  fileList: { marginTop: "24px" },
  fileGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "12px", marginTop: "12px" },
  fileItem: { display: "flex", justifyContent: "space-between", alignItems: "center", backgroundColor: "#fff", border: "1px solid #b2dfdb", borderRadius: "8px", padding: "12px" },
  fileName: { fontSize: "14px", flex: 1, marginRight: "8px", color: "#0f766e" },
  deleteButton: { border: "none", backgroundColor: "#ef4444", color: "white", borderRadius: "4px", padding: "4px 8px", cursor: "pointer", fontSize: "12px" },
  successStatus: { marginTop: "16px", padding: "12px", backgroundColor: "#dcfce7", color: "#166534", borderRadius: "8px", fontWeight: "500" },
  errorStatus: { marginTop: "16px", padding: "12px", backgroundColor: "#ffcdd2", color: "#c62828", borderRadius: "8px", fontWeight: "500" },
};
