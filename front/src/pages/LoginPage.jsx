import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    const registeredUserData = localStorage.getItem('registeredUser');
    if (!registeredUserData) {
      alert("Aucun compte trouvé. Veuillez d'abord vous inscrire.");
      navigate('/register');
      return;
    }

    const storedUser = JSON.parse(registeredUserData);

    if (storedUser.email !== email || storedUser.password !== password) {
      alert('Email ou mot de passe incorrect.');
      return;
    }

    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('userRole', storedUser.role);
    localStorage.setItem('userEmail', storedUser.email);
    localStorage.setItem('userName', storedUser.name);

    if (storedUser.role === 'operator') {
      navigate('/operator');
    } else if (storedUser.role === 'crm') {
      navigate('/crm');
    } else if (storedUser.role === 'compliance') {
      navigate('/compliance');
    }
  };

  return (
    <div className="page-center">
      <div className="card card-md">
        <h2 style={styles.title}>Connexion</h2>
        <p style={styles.subtitle}>Connectez-vous avec votre compte.</p>

        <form onSubmit={handleLogin} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              placeholder="exemple@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
              required
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Mot de passe</label>
            <input
              type="password"
              placeholder="********"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={styles.input}
              required
            />
          </div>

          <button type="submit" style={styles.button}>
            Se connecter
          </button>
        </form>

        <p style={styles.footerText}>
          Vous n'avez pas encore de compte ?{' '}
          <Link to="/register" style={styles.link}>
            S'inscrire
          </Link>
        </p>

        <Link className="back-link" to="/">
          ← Retour à l'accueil
        </Link>
      </div>
    </div>
  );
}

const styles = {
  title: {
    marginBottom: '10px',
    color: '#0f766e',
  },
  subtitle: {
    marginBottom: '24px',
    color: '#00695c',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '18px',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  label: {
    fontWeight: '600',
    color: '#0f766e',
  },
  input: {
    padding: '12px',
    border: '1px solid #b2dfdb',
    borderRadius: '8px',
    fontSize: '15px',
  },
  button: {
    marginTop: '10px',
    padding: '12px',
    backgroundColor: '#0f766e',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  footerText: {
    marginTop: '18px',
    color: '#00695c',
  },
  link: {
    color: '#0f766e',
    fontWeight: '600',
    textDecoration: 'none',
  },
};