// pages/RegisterPage.jsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await register(form.username, form.email, form.password);
      signIn(res.data.access_token, res.data.user);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.message || "Erro ao registrar.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="card auth-card">
        <h1>Criar conta</h1>
        <p>Acesse o Analisador de E-mails AutoU</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Usuário</label>
            <input value={form.username} onChange={set("username")} required autoFocus />
          </div>
          <div className="form-group">
            <label>E-mail</label>
            <input type="email" value={form.email} onChange={set("email")} required />
          </div>
          <div className="form-group">
            <label>Senha</label>
            <input type="password" value={form.password} onChange={set("password")} required />
          </div>
          {error && <div className="error-msg" style={{ marginBottom: "1rem" }}>{error}</div>}
          <button className="btn-primary" style={{ width: "100%" }} disabled={loading}>
            {loading ? "Criando..." : "Criar conta"}
          </button>
        </form>
        <p style={{ marginTop: "1rem", color: "var(--color-muted)", fontSize: "0.875rem" }}>
          Já tem conta? <Link to="/login">Entrar</Link>
        </p>
      </div>
    </div>
  );
}
