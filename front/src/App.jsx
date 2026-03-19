import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import Header from './components/Header';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import OperatorPage from './pages/OperatorPage';
import CRMPage from './pages/CRMPage';
import CompliancePage from './pages/CompliancePage';
import SupplierDetailPage from './pages/SupplierDetailPage';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/operator"
          element={
            <ProtectedRoute allowedRole="operator">
              <OperatorPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/crm"
          element={
            <ProtectedRoute allowedRole="supplier">
              <CRMPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/crm/:supplierId"
          element={
            <ProtectedRoute allowedRole="supplier">
              <SupplierDetailPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/compliance"
          element={
            <ProtectedRoute allowedRole="admin">
              <CompliancePage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
