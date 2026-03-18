import { useState } from 'react';

export default function UploadBox() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [status, setStatus] = useState('');

  const handleFileChange = (event) => {
    const newFiles = Array.from(event.target.files);

    setSelectedFiles((prevFiles) => {
      const existingNames = prevFiles.map((file) => file.name);

      const uniqueNewFiles = newFiles.filter(
        (file) => !existingNames.includes(file.name)
      );

      return [...prevFiles, ...uniqueNewFiles];
    });

    setStatus('');
    event.target.value = '';
  };

  const handleRemoveFile = (fileName) => {
    setSelectedFiles((prevFiles) =>
      prevFiles.filter((file) => file.name !== fileName)
    );
  };

  const handleUpload = () => {
    if (selectedFiles.length === 0) {
      setStatus('Aucun fichier sélectionné.');
      return;
    }

    setStatus('Documents envoyés avec succès.');
  };

  return (
    <div style={styles.container}>
      <div style={styles.uploadArea}>
        <div style={styles.uploadIcon}>📎</div>
        <h3>Sélectionnez vos documents</h3>
        <p>Glissez-déposez vos fichiers ou cliquez pour parcourir</p>
        <input
          type="file"
          multiple
          onChange={handleFileChange}
          style={styles.input}
        />
        <button onClick={handleUpload} style={styles.button}>
          Envoyer les documents
        </button>
      </div>

      {selectedFiles.length > 0 && (
        <div style={styles.fileList}>
          <h4>Fichiers sélectionnés ({selectedFiles.length})</h4>
          <div style={styles.fileGrid}>
            {selectedFiles.map((file, index) => (
              <div key={index} style={styles.fileItem}>
                <span style={styles.fileName}>{file.name}</span>
                <button
                  onClick={() => handleRemoveFile(file.name)}
                  style={styles.deleteButton}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {status && (
        <div style={styles.status}>
          {status}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    marginTop: '32px',
  },
  uploadArea: {
    border: '2px dashed #cbd5e1',
    borderRadius: '12px',
    padding: '40px',
    textAlign: 'center',
    backgroundColor: '#f8fafc',
    marginBottom: '24px',
  },
  uploadIcon: {
    fontSize: '48px',
    marginBottom: '16px',
  },
  input: {
    display: 'block',
    margin: '20px auto',
  },
  button: {
    padding: '12px 24px',
    border: 'none',
    borderRadius: '8px',
    backgroundColor: '#0f766e',
    color: 'white',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '600',
  },
  fileList: {
    marginTop: '24px',
  },
  fileGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '12px',
    marginTop: '12px',
  },
  fileItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    padding: '12px',
  },
  fileName: {
    fontSize: '14px',
    flex: 1,
    marginRight: '8px',
  },
  deleteButton: {
    border: 'none',
    backgroundColor: '#ef4444',
    color: 'white',
    borderRadius: '4px',
    padding: '4px 8px',
    cursor: 'pointer',
    fontSize: '12px',
  },
  status: {
    marginTop: '16px',
    padding: '12px',
    backgroundColor: '#dcfce7',
    color: '#166534',
    borderRadius: '8px',
    fontWeight: '500',
  },
};