// pages/AnalyzePage.jsx — Triagem de emails enterprise com IA, NER, Sentimento, Fraude, Tons e Workflow
import { useState, useRef, useEffect } from "react";
import {
  analyzeEmail,
  analyzeWithFile,
  regenerateTone,
  getNotes,
  addNote,
  updateAnalysisStatus,
} from "../api/analyze";
import { submitFeedback } from "../api/stats";

const TONES = [
  { id: "formal", label: "Formal" },
  { id: "empatico", label: "Empático" },
  { id: "negociacao", label: "Negociação" },
  { id: "juridico", label: "Jurídico" },
  { id: "direto", label: "Direto" },
];

const STATUSES = [
  { id: "pending", label: "Pendente" },
  { id: "in_progress", label: "Em Andamento" },
  { id: "resolved", label: "Resolvido" },
  { id: "escalated", label: "Escalado" },
];

export default function AnalyzePage() {
  const [subject, setSubject] = useState("");
  const [senderEmail, setSenderEmail] = useState("");
  const [emailContent, setEmailContent] = useState("");
  const [selectedTone, setSelectedTone] = useState("formal");
  const [useThreadContext, setUseThreadContext] = useState(true);
  const [file, setFile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Regeneração de tom
  const [activeTone, setActiveTone] = useState("formal");
  const [regeneratingTone, setRegeneratingTone] = useState(false);

  // Workflow & Notas
  const [currentStatus, setCurrentStatus] = useState("pending");
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState("");
  const [submittingNote, setSubmittingNote] = useState(false);

  // Feedback Human-in-the-Loop
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [correcting, setCorrecting] = useState(false);
  const [correctedCategory, setCorrectedCategory] = useState("");

  const fileRef = useRef();

  const loadNotes = async (analysisId) => {
    if (!analysisId) return;
    try {
      const res = await getNotes(analysisId);
      setNotes(res.data.notes || []);
    } catch {
      // Falha silenciosa em notas
    }
  };

  useEffect(() => {
    if (result?.id || result?.analysis_id) {
      const id = result.id || result.analysis_id;
      setCurrentStatus(result.status || "pending");
      setActiveTone(result.tone_used || selectedTone);
      loadNotes(id);
    }
  }, [result]);

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
        if (emailContent) {
          fd.append("text", emailContent);
          fd.append("email_content", emailContent);
        }
        if (subject) fd.append("subject", subject);
        if (senderEmail) fd.append("sender_email", senderEmail);
        fd.append("tone", selectedTone);
        res = await analyzeWithFile(fd);
      } else {
        res = await analyzeEmail(
          emailContent,
          senderEmail || null,
          subject || null,
          selectedTone,
          useThreadContext
        );
      }
      setResult(res.data);
    } catch (err) {
      const data = err.response?.data;
      if (data?.details) {
        const detailsStr = Object.entries(data.details)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
          .join(" | ");
        setError(`${data.error || "Erro de validação"}: ${detailsStr}`);
      } else {
        setError(data?.error || data?.message || "Erro ao analisar o e-mail.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateTone = async (newTone) => {
    const analysisId = result?.id || result?.analysis_id;
    if (!analysisId) return;
    setRegeneratingTone(true);
    try {
      const res = await regenerateTone(analysisId, newTone);
      setResult((prev) => ({
        ...prev,
        suggested_response: res.data.suggested_response,
        tone_used: res.data.tone_used,
      }));
      setActiveTone(newTone);
    } catch {
      setError("Erro ao regenerar tom da resposta.");
    } finally {
      setRegeneratingTone(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    const analysisId = result?.id || result?.analysis_id;
    if (!analysisId) return;
    try {
      await updateAnalysisStatus(analysisId, newStatus);
      setCurrentStatus(newStatus);
      setResult((prev) => ({ ...prev, status: newStatus }));
    } catch {
      setError("Não foi possível atualizar o status.");
    }
  };

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNote.trim()) return;
    const analysisId = result?.id || result?.analysis_id;
    if (!analysisId) return;
    setSubmittingNote(true);
    try {
      await addNote(analysisId, newNote.trim());
      setNewNote("");
      loadNotes(analysisId);
    } catch {
      setError("Erro ao adicionar nota interna.");
    } finally {
      setSubmittingNote(false);
    }
  };

  const handleFeedback = async (approved) => {
    const analysisId = result?.id || result?.analysis_id;
    if (!analysisId) return;
    setFeedbackLoading(true);
    try {
      await submitFeedback(
        analysisId,
        approved,
        approved ? null : correctedCategory || null
      );
      setFeedbackSent(true);
      setCorrecting(false);
    } catch {
      // feedback não crítico
    } finally {
      setFeedbackLoading(false);
    }
  };

  const getUrgencyClass = (urgency) => {
    const u = (urgency || "").toLowerCase();
    if (u.includes("critica") || u.includes("crítica")) return "badge-urgency-critica";
    if (u.includes("alta")) return "badge-urgency-alta";
    if (u.includes("media") || u.includes("média")) return "badge-urgency-media";
    return "badge-urgency-baixa";
  };

  const getSentimentClass = (sentiment) => {
    const s = (sentiment || "").toLowerCase();
    if (s.includes("positivo")) return "badge-sentiment-positivo";
    if (s.includes("irritado")) return "badge-sentiment-irritado";
    if (s.includes("negativo")) return "badge-sentiment-negativo";
    return "badge-sentiment-neutro";
  };

  const categoryClass =
    result?.category === "Produtivo" ? "badge-productive" : "badge-unproductive";

  return (
    <div>
      <div className="page-header">
        <h1>Análise & Triagem Corporativa de E-mails</h1>
        <p>Motor de IA com extração de NER, sentimento, urgência, antifraude e governança LGPD.</p>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <div className="form-group">
              <label>Assunto do E-mail</label>
              <input
                type="text"
                placeholder="Ex: Urgente: Regularização de Contrato #4912"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Remetente (E-mail)</label>
              <input
                type="email"
                placeholder="cliente@empresa.com.br"
                value={senderEmail}
                onChange={(e) => setSenderEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label>Conteúdo do E-mail</label>
            <textarea
              className="analyzer-textarea"
              placeholder="Cole aqui o corpo do e-mail recebido..."
              value={emailContent}
              onChange={(e) => setEmailContent(e.target.value)}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", alignItems: "center" }}>
            <div className="form-group">
              <label>Tom de Resposta Desejado</label>
              <div className="tone-selector">
                {TONES.map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    className={`tone-chip ${selectedTone === t.id ? "active" : ""}`}
                    onClick={() => setSelectedTone(t.id)}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Anexar Arquivo (.EML, .PDF ou .TXT)</label>
              <input
                ref={fileRef}
                type="file"
                accept=".eml,.pdf,.txt"
                onChange={(e) => setFile(e.target.files[0] || null)}
              />
              {file && (
                <span style={{ fontSize: "0.8rem", color: "var(--color-muted)" }}>
                  {file.name}{" "}
                  <button
                    type="button"
                    className="btn-ghost"
                    style={{ padding: "0.1rem 0.4rem", fontSize: "0.75rem" }}
                    onClick={() => {
                      setFile(null);
                      fileRef.current.value = "";
                    }}
                  >
                    remover
                  </button>
                </span>
              )}
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", margin: "1rem 0" }}>
            <input
              type="checkbox"
              id="threadContext"
              checked={useThreadContext}
              onChange={(e) => setUseThreadContext(e.target.checked)}
              style={{ width: "auto" }}
            />
            <label htmlFor="threadContext" style={{ fontSize: "0.85rem", color: "var(--color-muted)", cursor: "pointer" }}>
              Utilizar memória de thread (busca últimas 5 mensagens para contexto contínuo)
            </label>
          </div>

          {error && <div className="error-msg" style={{ marginBottom: "1rem" }}>{error}</div>}

          <button
            className="btn-primary"
            disabled={loading || (!emailContent && !file)}
            style={{ width: "100%", padding: "0.8rem" }}
          >
            {loading ? "Processando e Analisando com IA..." : "Executar Análise & Triagem"}
          </button>
        </form>
      </div>

      {loading && <div className="spinner" />}

      {result && (
        <div className="card result-card">
          {/* Header com Categoria e Badges de Inteligência */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
                <span className={`badge ${categoryClass}`} style={{ fontSize: "0.9rem" }}>
                  {result.category}
                </span>
                {result.urgency && (
                  <span className={`badge ${getUrgencyClass(result.urgency)}`}>
                    Urgência: {result.urgency}
                  </span>
                )}
                {result.sentiment && (
                  <span className={`badge ${getSentimentClass(result.sentiment)}`}>
                    Sentimento: {result.sentiment}
                  </span>
                )}
                {result.pii_masked && (
                  <span className="badge" style={{ background: "rgba(88,166,255,0.15)", color: "var(--color-primary)" }}>
                    🛡️ PII Sanitizado
                  </span>
                )}
              </div>
            </div>

            {/* Controle de Status do Chamado */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "0.82rem", color: "var(--color-muted)" }}>Status:</span>
              <select
                value={currentStatus}
                onChange={(e) => handleStatusChange(e.target.value)}
                style={{ width: "auto", padding: "0.3rem 0.6rem", fontSize: "0.85rem" }}
              >
                {STATUSES.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Alerta de Fraude / Phishing */}
          {(result.fraud_risk_score > 0.4 || (result.fraud_flags && result.fraud_flags.length > 0)) && (
            <div className="alert-banner alert-fraud" style={{ marginTop: "1.25rem" }}>
              <div>
                <strong>⚠️ Alerta de Segurança / Risco de Fraude (Score: {((result.fraud_risk_score || 0) * 100).toFixed(0)}%)</strong>
                {result.fraud_flags && result.fraud_flags.length > 0 && (
                  <p style={{ fontSize: "0.85rem", marginTop: "0.25rem" }}>
                    Indícios detectados: {result.fraud_flags.join(" · ")}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Alerta de Quarentena Humana */}
          {result.in_quarantine && (
            <div className="alert-banner alert-quarantine" style={{ marginTop: "1rem" }}>
              <div>
                <strong>🛡️ Email em Quarentena Humana</strong>
                <p style={{ fontSize: "0.85rem", marginTop: "0.2rem" }}>
                  A confiança do modelo ficou abaixo do limiar de segurança ({((result.confidence_score || 0) * 100).toFixed(0)}%). Exige validação prévia de um operador antes de envio.
                </p>
              </div>
            </div>
          )}

          {/* Resumo */}
          <div className="result-section">
            <h4>Resumo Executivo</h4>
            <p>{result.summary}</p>
          </div>

          {/* Entidades Extraídas (NER) */}
          {result.extracted_entities && Object.keys(result.extracted_entities).length > 0 && (
            <div className="result-section">
              <h4>Entidades Nomeadas Extraídas (NER)</h4>
              <div className="ner-grid">
                {result.extracted_entities.valores && result.extracted_entities.valores.length > 0 && (
                  <div className="ner-card">
                    <div className="ner-card-title">Valores Monetários</div>
                    {result.extracted_entities.valores.map((v, i) => (
                      <span key={i} className="ner-tag">{v}</span>
                    ))}
                  </div>
                )}
                {result.extracted_entities.datas && result.extracted_entities.datas.length > 0 && (
                  <div className="ner-card">
                    <div className="ner-card-title">Datas & Prazos</div>
                    {result.extracted_entities.datas.map((d, i) => (
                      <span key={i} className="ner-tag">{d}</span>
                    ))}
                  </div>
                )}
                {result.extracted_entities.documentos && result.extracted_entities.documentos.length > 0 && (
                  <div className="ner-card">
                    <div className="ner-card-title">Documentos / CNPJ / CPF</div>
                    {result.extracted_entities.documentos.map((doc, i) => (
                      <span key={i} className="ner-tag">{doc}</span>
                    ))}
                  </div>
                )}
                {result.extracted_entities.protocolos && result.extracted_entities.protocolos.length > 0 && (
                  <div className="ner-card">
                    <div className="ner-card-title">Protocolos & Contratos</div>
                    {result.extracted_entities.protocolos.map((p, i) => (
                      <span key={i} className="ner-tag">{p}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Sugestão de Resposta com Seletor de Tom Dinâmico */}
          {result.suggested_response && (
            <div className="result-section">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                <h4>Sugestão de Resposta com IA</h4>
                <div style={{ display: "flex", gap: "0.35rem", alignItems: "center" }}>
                  <span style={{ fontSize: "0.75rem", color: "var(--color-muted)" }}>Tom:</span>
                  {TONES.map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      disabled={regeneratingTone}
                      className={`tone-chip ${activeTone === t.id ? "active" : ""}`}
                      style={{ padding: "0.2rem 0.5rem", fontSize: "0.75rem" }}
                      onClick={() => handleRegenerateTone(t.id)}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>
              <p style={{ whiteSpace: "pre-wrap", background: "var(--color-bg)", padding: "1rem", borderRadius: "var(--radius)", border: "1px solid var(--color-border)" }}>
                {regeneratingTone ? "Regenerando resposta no novo tom..." : result.suggested_response}
              </p>
            </div>
          )}

          {/* Metadados Técnicos */}
          {result.model_used && (
            <p style={{ fontSize: "0.78rem", color: "var(--color-muted)", marginTop: "1rem" }}>
              Modelo: {result.model_used}
              {result.processing_time_ms && ` · ${result.processing_time_ms}ms`}
              {result.cached && " · cache hit ✓"}
              {result.confidence_score && ` · Confiança: ${((result.confidence_score) * 100).toFixed(0)}%`}
            </p>
          )}

          {/* Notas Internas da Equipe */}
          <div className="notes-container">
            <h4 style={{ color: "var(--color-muted)", fontSize: "0.8rem", textTransform: "uppercase", marginBottom: "0.75rem" }}>
              Notas Internas da Equipe (Privadas)
            </h4>
            {notes.length === 0 ? (
              <p style={{ fontSize: "0.85rem", color: "var(--color-muted)", marginBottom: "0.75rem" }}>
                Nenhuma anotação nesta thread ainda.
              </p>
            ) : (
              <div style={{ marginBottom: "0.75rem" }}>
                {notes.map((n) => (
                  <div key={n.id} className="note-item">
                    <div className="note-meta">
                      <strong>{n.user_name || "Operador"}</strong> · {new Date(n.created_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}
                    </div>
                    <div>{n.content}</div>
                  </div>
                ))}
              </div>
            )}
            <form onSubmit={handleAddNote} style={{ display: "flex", gap: "0.5rem" }}>
              <input
                type="text"
                placeholder="Adicionar nota interna para o time..."
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                style={{ fontSize: "0.85rem" }}
              />
              <button
                type="submit"
                className="btn-ghost"
                disabled={submittingNote || !newNote.trim()}
                style={{ padding: "0.4rem 1rem", fontSize: "0.85rem", whiteSpace: "nowrap" }}
              >
                {submittingNote ? "Salvando..." : "Adicionar"}
              </button>
            </form>
          </div>

          {/* Feedback Human-in-the-Loop */}
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
                ✓ Sim, Correto
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
                  <input
                    type="text"
                    placeholder="Categoria correta..."
                    value={correctedCategory}
                    onChange={(e) => setCorrectedCategory(e.target.value)}
                    style={{ width: "auto" }}
                  />
                  <button
                    className="btn-danger"
                    disabled={feedbackLoading || !correctedCategory.trim()}
                    onClick={() => handleFeedback(false)}
                  >
                    Enviar Correção
                  </button>
                </div>
              )}
            </div>
          ) : (
            <p style={{ marginTop: "1.25rem", color: "var(--color-success)", fontSize: "0.875rem" }}>
              ✓ Feedback registrado com sucesso para melhoria contínua.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
