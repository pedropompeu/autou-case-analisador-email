// pages/LoginPage.jsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await login(username, password);
      signIn(res.data.access_token, res.data.user || { username: res.data.username, role: res.data.role });
      navigate("/");
    } catch (err) {
      const data = err.response?.data;
      setError(data?.error || data?.message || "Credenciais inválidas.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="card auth-card">
        <h1>Entrar</h1>
        <p>Acesse o Analisador de E-mails AutoU</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Usuário</label>
            <input value={username} onChange={(e) => setUsername(e.target.value)} required autoFocus />
          </div>
          <div className="form-group">
            <label>Senha</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          {error && <div className="error-msg" style={{ marginBottom: "1rem" }}>{error}</div>}
          <button className="btn-primary" style={{ width: "100%" }} disabled={loading}>
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
        <p style={{ marginTop: "1rem", color: "var(--color-muted)", fontSize: "0.875rem" }}>
          Não tem conta? <Link to="/register">Registre-se</Link>
        </p>
      </div>
    </div>
  );
}
