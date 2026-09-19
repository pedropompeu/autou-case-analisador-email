// App.jsx — Roteamento principal e shell da aplicação corporativa
import { BrowserRouter, Routes, Route, Navigate, NavLink } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import AnalyzePage from "./pages/AnalyzePage";
import DashboardPage from "./pages/DashboardPage";
import IntegrationsPage from "./pages/IntegrationsPage";
import CompliancePage from "./pages/CompliancePage";
import "./App.css";

// Guard para rotas protegidas
function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="spinner" style={{ marginTop: "4rem" }} />;
  return user ? children : <Navigate to="/login" replace />;
}

function Navbar() {
  const { user, signOut } = useAuth();
  if (!user) return null;
  return (
    <nav className="navbar">
      <span className="navbar-brand">AutoU <span>Email Analyzer Enterprise</span></span>
      <div className="navbar-nav">
        <NavLink to="/" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`} end>
          Triagem IA
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
          Dashboard ROI
        </NavLink>
        <NavLink to="/integrations" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
          Automações & APIs
        </NavLink>
        <NavLink to="/compliance" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
          Governança LGPD
        </NavLink>
        <button
          className="btn-ghost"
          style={{ padding: "0.35rem 0.8rem", fontSize: "0.85rem", marginLeft: "0.5rem" }}
          onClick={signOut}
        >
          Sair ({user.username})
        </button>
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="app-shell">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route
                path="/"
                element={<PrivateRoute><AnalyzePage /></PrivateRoute>}
              />
              <Route
                path="/dashboard"
                element={<PrivateRoute><DashboardPage /></PrivateRoute>}
              />
              <Route
                path="/integrations"
                element={<PrivateRoute><IntegrationsPage /></PrivateRoute>}
              />
              <Route
                path="/compliance"
                element={<PrivateRoute><CompliancePage /></PrivateRoute>}
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}
