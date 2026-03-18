import { Link, useLocation, useNavigate } from 'react-router-dom';
import { documents } from '../data/mockData';

export default function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const anomaliesCount = documents.filter((doc) => doc.anomaly !== 'Aucune').length;
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  const userRole = localStorage.getItem('userRole');

  const handleLogout = () => {
  localStorage.removeItem('isAuthenticated');
  localStorage.removeItem('userRole');
  localStorage.removeItem('userEmail');
  localStorage.removeItem('userName');

  navigate('/');
  window.location.reload();
};

  // Déterminer le nom de la page selon le rôle
  const getPageName = () => {
    switch (userRole) {
      case 'operator':
        return 'Opérateur';
      case 'crm':
        return 'CRM';
      case 'compliance':
        return 'Conformité';
      default:
        return '';
    }
  };

  // Déterminer la page d'accueil selon le rôle
  const getDefaultPage = () => {
    switch (userRole) {
      case 'operator':
        return '/operator';
      case 'crm':
        return '/crm';
      case 'compliance':
        return '/compliance';
      default:
        return '/';
    }
  };

  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          Plateforme Conformité
        </Link>

        {isAuthenticated && (
          <>
            <div style={styles.profileSection}>
              <Link 
                to={getDefaultPage()} 
                style={styles.pageButton}
              >
                📄 {getPageName()}
              </Link>
              <Link to="/profile" style={styles.profileLink}>
                👤 Profil
              </Link>
              <button style={styles.logoutButton} onClick={handleLogout}>
                🚪 Se déconnecter
              </button>
            </div>
          </>
        )}
      </div>
    </header>
  );
}

const styles = {
  navBadge: {
    padding: '4px 12px',
    backgroundColor: '#ef5350',
    color: 'white',
    borderRadius: '20px',
    fontSize: '12px',
    fontWeight: '600',
    marginRight: '8px',
  },
  profileSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    marginLeft: 'auto',
  },
  pageButton: {
    fontSize: '13px',
    color: '#0f766e',
    fontWeight: '500',
    textDecoration: 'none',
    padding: '6px 12px',
    borderRadius: '6px',
    transition: 'all 0.3s ease',
    border: '1px solid #0f766e',
  },
  profileLink: {
    fontSize: '13px',
    color: '#0f766e',
    fontWeight: '500',
    textDecoration: 'none',
    padding: '6px 12px',
    borderRadius: '6px',
    transition: 'all 0.3s ease',
    border: '1px solid #b2dfdb',
  },
  logoutButton: {
    fontSize: '13px',
    color: '#c62828',
    fontWeight: '500',
    padding: '6px 12px',
    borderRadius: '6px',
    border: '1px solid #ef5350',
    backgroundColor: 'transparent',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  },
};