import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('operator');

  const navigate = useNavigate();

  const handleRegister = (e) => {
    e.preventDefault();

    const newUser = {
      name,
      email,
      password,
      role,
    };

    localStorage.setItem('registeredUser', JSON.stringify(newUser));

    navigate('/login');
  };

  return (
    <div className="page-center">
      <div className="card card-md">
        <h2 style={styles.title}>Inscription</h2>
        <p style={styles.subtitle}>Créez votre compte pour accéder à la plateforme.</p>

        <form onSubmit={handleRegister} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Nom</label>
            <input
              type="text"
              placeholder="Votre nom"
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={styles.input}
              required
            />
          </div>

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

          <div style={styles.field}>
            <label style={styles.label}>Rôle</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              style={styles.input}
            >
              <option value="operator">Opérateur</option>
              <option value="crm">Comptable / CRM</option>
              <option value="compliance">Conformité</option>
            </select>
          </div>

          <button type="submit" style={styles.button}>
            S'inscrire
          </button>
        </form>

        <p style={styles.footerText}>
          Vous avez déjà un compte ?{' '}
          <Link to="/login" style={styles.link}>
            Se connecter
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