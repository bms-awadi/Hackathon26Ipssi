import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';

export default function ProfilePage() {
  const navigate = useNavigate();
  const [userName, setUserName] = useState(localStorage.getItem('userName') || '');
  const [userEmail, setUserEmail] = useState(localStorage.getItem('userEmail') || '');
  const [isEditing, setIsEditing] = useState(false);
  const userRole = localStorage.getItem('userRole');

  const handleSave = () => {
    localStorage.setItem('userName', userName);
    localStorage.setItem('userEmail', userEmail);
    
    // Mettre à jour aussi dans registeredUser
    const registeredUserData = localStorage.getItem('registeredUser');
    if (registeredUserData) {
      const registeredUser = JSON.parse(registeredUserData);
      registeredUser.name = userName;
      registeredUser.email = userEmail;
      localStorage.setItem('registeredUser', JSON.stringify(registeredUser));
    }
    
    setIsEditing(false);
    alert('Profil mis à jour avec succès!');
  };

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userName');
    navigate('/');
  };

  const getRoleLabel = (role) => {
    const roleLabels = {
      operator: 'Opérateur',
      crm: 'Comptable / CRM',
      compliance: 'Conformité',
      operateur: 'Opérateur',
      responsable: 'Responsable',
      manager: 'Manager',
      auditeur: 'Auditeur',
    };
    return roleLabels[role] || role;
  };

  return (
    <div className="page">
      <div className="card card-md">
        <div style={styles.header}>
          <h2>👤 Mon profil</h2>
          <p>Consultez et gérez vos informations personnelles.</p>
        </div>

        <div style={styles.profileInfo}>
          <div style={styles.infoCard}>
            <label style={styles.label}>Nom</label>
            {isEditing ? (
              <input
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                style={styles.input}
              />
            ) : (
              <div style={styles.value}>{userName || 'Non défini'}</div>
            )}
          </div>

          <div style={styles.infoCard}>
            <label style={styles.label}>Email</label>
            {isEditing ? (
              <input
                type="email"
                value={userEmail}
                onChange={(e) => setUserEmail(e.target.value)}
                style={styles.input}
              />
            ) : (
              <div style={styles.value}>{userEmail || 'Non défini'}</div>
            )}
          </div>

          <div style={styles.infoCard}>
            <label style={styles.label}>Rôle</label>
            <div style={styles.value}>{getRoleLabel(userRole)}</div>
          </div>
        </div>

        <div style={styles.actions}>
          {!isEditing ? (
            <button style={styles.editButton} onClick={() => setIsEditing(true)}>
              ✏️ Modifier
            </button>
          ) : (
            <>
              <button style={styles.saveButton} onClick={handleSave}>
                💾 Enregistrer
              </button>
              <button style={styles.cancelButton} onClick={() => setIsEditing(false)}>
                ✕ Annuler
              </button>
            </>
          )}
          <button style={styles.logoutButton} onClick={handleLogout}>
            🚪 Se déconnecter
          </button>
        </div>

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
  profileInfo: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '1rem',
    marginBottom: '2rem',
  },
  infoCard: {
    padding: '1.5rem',
    backgroundColor: '#f0fffe',
    border: '1px solid #b2dfdb',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(15, 118, 110, 0.08)',
  },
  label: {
    display: 'block',
    fontSize: '0.875rem',
    color: '#00695c',
    fontWeight: '600',
    marginBottom: '0.5rem',
  },
  value: {
    fontSize: '1rem',
    color: '#0f766e',
    fontWeight: '500',
  },
  actions: {
    display: 'flex',
    gap: '1rem',
    marginBottom: '1.5rem',
    flexWrap: 'wrap',
  },
  input: {
    width: '100%',
    padding: '0.75rem',
    fontSize: '1rem',
    border: '1px solid #b2dfdb',
    borderRadius: '6px',
    fontFamily: 'inherit',
    boxSizing: 'border-box',
  },
  editButton: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#0f766e',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '0.95rem',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
  },
  saveButton: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#2e7d32',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '0.95rem',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
  },
  cancelButton: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#f5f5f5',
    color: '#666',
    border: '1px solid #ccc',
    borderRadius: '6px',
    fontSize: '0.95rem',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
  logoutButton: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#c62828',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '0.95rem',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
  },
};
