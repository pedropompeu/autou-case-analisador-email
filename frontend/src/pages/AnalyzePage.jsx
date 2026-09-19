// pages/AnalyzePage.jsx — Formulário de análise com feedback human-in-the-loop
import { useState, useRef } from "react";
import { analyzeEmail, analyzeWithFile } from "../api/analyze";
import { submitFeedback } from "../api/stats";

const CATEGORIES = ["Produtivo", "Improdutivo"];

export default function AnalyzePage() {
  const [emailContent, setEmailContent] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [correcting, setCorrecting] = useState(false);
  const [correctedCategory, setCorrectedCategory] = useState("");
  const fileRef = useRef();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setFeedbackSent(false);
    setLoading(true);
    try {
      let res;
      if (file) {
        const fd = new FormData();
        fd.append("file", file);
        if (emailContent) fd.append("email_content", emailContent);
        res = await analyzeWithFile(fd);
      } else {
        res = await analyzeEmail(emailContent);
      }
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.message || "Erro ao analisar o e-mail.");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (approved) => {
    setFeedbackLoading(true);
    try {
      await submitFeedback(
        result.analysis_id ?? result.id,
        approved,
        approved ? null : correctedCategory || null
      );
      setFeedbackSent(true);
      setCorrecting(false);
    } catch {
      // feedback não crítico — não bloqueia UX
    } finally {
      setFeedbackLoading(false);
    }
  };

  const categoryClass = result?.category === "Produtivo" ? "badge-productive" : "badge-unproductive";

  return (
    <div>
      <div className="page-header">
        <h1>Analisador de E-mails</h1>
        <p>Cole o conteúdo do e-mail ou anexe um arquivo PDF/TXT para análise pela IA.</p>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Conteúdo do e-mail</label>
            <textarea
              className="analyzer-textarea"
              placeholder="Cole aqui o corpo do e-mail..."
              value={emailContent}
              onChange={(e) => setEmailContent(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Arquivo anexo (PDF ou TXT — opcional)</label>
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.txt"
              onChange={(e) => setFile(e.target.files[0] || null)}
            />
            {file && (
              <span style={{ fontSize: "0.8rem", color: "var(--color-muted)", marginTop: "0.25rem" }}>
                {file.name}{" "}
                <button
                  type="button"
                  className="btn-ghost"
                  style={{ padding: "0.1rem 0.5rem", fontSize: "0.75rem" }}
                  onClick={() => { setFile(null); fileRef.current.value = ""; }}
                >
                  remover
                </button>
              </span>
            )}
          </div>

          {error && <div className="error-msg" style={{ marginBottom: "1rem" }}>{error}</div>}

          <button
            className="btn-primary"
            disabled={loading || (!emailContent && !file)}
          >
            {loading ? "Analisando..." : "Analisar"}
          </button>
        </form>
      </div>

      {loading && <div className="spinner" />}

      {result && (
        <div className="card result-card">
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <h3>Resultado</h3>
            <span className={`badge ${categoryClass}`}>{result.category}</span>
          </div>

          <div className="result-section">
            <h4>Resumo</h4>
            <p>{result.summary}</p>
          </div>

          {result.suggested_response && (
            <div className="result-section">
              <h4>Resposta sugerida</h4>
              <p style={{ whiteSpace: "pre-wrap" }}>{result.suggested_response}</p>
            </div>
          )}

          {result.model_used && (
            <p style={{ fontSize: "0.78rem", color: "var(--color-muted)", marginTop: "1rem" }}>
              Modelo: {result.model_used}
              {result.processing_time_ms && ` · ${result.processing_time_ms}ms`}
              {result.cached && " · cache hit ✓"}
            </p>
          )}

          {/* Feedback human-in-the-loop */}
          {!feedbackSent ? (
            <div className="feedback-row">
              <span style={{ color: "var(--color-muted)", fontSize: "0.875rem", alignSelf: "center" }}>
                Esta classificação está correta?
              </span>
              <button
                className="btn-success"
                disabled={feedbackLoading}
                onClick={() => handleFeedback(true)}
              >
                ✓ Sim
              </button>
              <button
                className="btn-ghost"
                disabled={feedbackLoading}
                onClick={() => setCorrecting(true)}
              >
                ✗ Corrigir
              </button>
              {correcting && (
                <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                  <select
                    value={correctedCategory}
                    onChange={(e) => setCorrectedCategory(e.target.value)}
                    style={{ width: "auto" }}
                  >
                    <option value="">Categoria correta...</option>
                    {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
                  </select>
                  <button
                    className="btn-danger"
                    disabled={feedbackLoading}
                    onClick={() => handleFeedback(false)}
                  >
                    Enviar correção
                  </button>
                </div>
              )}
            </div>
          ) : (
            <p style={{ marginTop: "1.25rem", color: "var(--color-success)", fontSize: "0.875rem" }}>
              ✓ Feedback registrado. Obrigado!
            </p>
          )}
        </div>
      )}
    </div>
  );
}
