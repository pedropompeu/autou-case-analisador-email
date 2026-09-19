// pages/CompliancePage.jsx — Central de Governança, LGPD e Trilha de Auditoria
import { useState, useEffect } from "react";
import {
  exportSubjectData,
  eraseSubjectData,
  getAuditLogs,
} from "../api/integrations";

export default function CompliancePage() {
  const [activeTab, setActiveTab] = useState("lgpd");
  const [subjectIdentifier, setSubjectIdentifier] = useState("");
  const [exportData, setExportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Audit Logs
  const [auditLogs, setAuditLogs] = useState([]);
  const [loadingAudit, setLoadingAudit] = useState(false);

  const loadAuditLogs = async () => {
    setLoadingAudit(true);
    try {
      const res = await getAuditLogs(50);
      setAuditLogs(res.data.audit_logs || []);
    } catch {
      setError("Acesso restrito: apenas Administradores e Auditores podem ver a trilha de auditoria.");
    } finally {
      setLoadingAudit(false);
    }
  };

  useEffect(() => {
    if (activeTab === "audit") {
      loadAuditLogs();
    }
    setError(null);
    setSuccessMsg(null);
  }, [activeTab]);

  const handleExport = async (e) => {
    e.preventDefault();
    if (!subjectIdentifier.trim()) return;
    setLoading(true);
    setError(null);
    setExportData(null);
    try {
      const res = await exportSubjectData(subjectIdentifier.trim());
      setExportData(res.data);
      setSuccessMsg("Relatório de dados do titular gerado com sucesso.");
    } catch (err) {
      setError(err.response?.data?.message || "Erro ao exportar dados do titular.");
    } finally {
      setLoading(false);
    }
  };

  const handleErase = async () => {
    if (!subjectIdentifier.trim()) return;
    const confirm = window.confirm(
      `ATENÇÃO: Deseja solicitar o Direito ao Esquecimento para '${subjectIdentifier}'? Todos os registros serão anonimizados irreversivelmente.`
    );
    if (!confirm) return;

    setLoading(true);
    setError(null);
    try {
      const res = await eraseSubjectData(subjectIdentifier.trim());
      setSuccessMsg(
        `Direito ao Esquecimento executado com sucesso: ${res.data.records_anonymized} registros anonimizados.`
      );
      setExportData(null);
    } catch (err) {
      setError(err.response?.data?.message || "Erro ao anonimizar dados.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Central de Governança & Compliance LGPD</h1>
        <p>Direito ao esquecimento, exportação de dados do titular (Art. 18/19) e trilha de auditoria imutável.</p>
      </div>

      <div className="tabs-nav">
        <button
          className={`tab-btn ${activeTab === "lgpd" ? "active" : ""}`}
          onClick={() => setActiveTab("lgpd")}
        >
          🛡️ Direitos do Titular (LGPD)
        </button>
        <button
          className={`tab-btn ${activeTab === "audit" ? "active" : ""}`}
          onClick={() => setActiveTab("audit")}
        >
          📋 Trilha de Auditoria Imutável
        </button>
      </div>

      {successMsg && (
        <div style={{ background: "rgba(63,185,80,0.15)", color: "var(--color-success)", padding: "0.75rem", borderRadius: "var(--radius)", marginBottom: "1rem" }}>
          ✓ {successMsg}
        </div>
      )}
      {error && <div className="error-msg" style={{ marginBottom: "1rem" }}>{error}</div>}

      {/* ABA: LGPD */}
      {activeTab === "lgpd" && (
        <div>
          <div className="card" style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>Consulta e Operações de Titular</h3>
            <p style={{ color: "var(--color-muted)", fontSize: "0.85rem", marginBottom: "1rem" }}>
              Informe o e-mail, CPF ou identificador do titular de dados para localizar ou expurgar ocorrências.
            </p>

            <form onSubmit={handleExport}>
              <div className="form-group">
                <label>Identificador do Titular (E-mail ou Documento)</label>
                <input
                  type="text"
                  placeholder="exemplo@cliente.com.br ou 123.456.789-00"
                  value={subjectIdentifier}
                  onChange={(e) => setSubjectIdentifier(e.target.value)}
                />
              </div>

              <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
                <button className="btn-primary" disabled={loading || !subjectIdentifier.trim()}>
                  {loading ? "Localizando..." : "📥 Exportar Dados do Titular (Art. 19)"}
                </button>
                <button
                  type="button"
                  className="btn-danger"
                  disabled={loading || !subjectIdentifier.trim()}
                  onClick={handleErase}
                >
                  🗑️ Direito ao Esquecimento (Art. 18)
                </button>
              </div>
            </form>
          </div>

          {exportData && (
            <div className="card result-card">
              <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
                Relatório de Dados do Titular ({exportData.total_records} registros encontrados)
              </h3>
              {exportData.records && exportData.records.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                  {exportData.records.map((r) => (
                    <div key={r.id} style={{ background: "var(--color-bg)", padding: "0.75rem 1rem", borderRadius: "var(--radius)", border: "1px solid var(--color-border)" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "var(--color-muted)" }}>
                        <span>ID #{r.id} · Categoria: {r.category}</span>
                        <span>{new Date(r.created_at).toLocaleDateString("pt-BR")}</span>
                      </div>
                      <div style={{ marginTop: "0.4rem", fontSize: "0.85rem" }}>
                        <strong>Resumo:</strong> {r.summary}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: "var(--color-muted)" }}>Nenhum registro ativo vinculado a este titular.</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* ABA: AUDITORIA */}
      {activeTab === "audit" && (
        <div className="card">
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Trilha de Auditoria do Tenant (Últimos 50 eventos)</h3>
          {loadingAudit ? (
            <div className="spinner" />
          ) : auditLogs.length === 0 ? (
            <p style={{ color: "var(--color-muted)" }}>Nenhum log registrado ainda.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Data/Hora</th>
                  <th>Ação</th>
                  <th>Recurso</th>
                  <th>Usuário</th>
                  <th>IP</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.id}>
                    <td style={{ fontSize: "0.78rem" }}>
                      {new Date(log.created_at).toLocaleString("pt-BR")}
                    </td>
                    <td>
                      <span className="badge" style={{ background: "rgba(88,166,255,0.15)", color: "var(--color-primary)" }}>
                        {log.action}
                      </span>
                    </td>
                    <td>{log.resource_type} {log.resource_id ? `#${log.resource_id}` : ""}</td>
                    <td>{log.user_id ? `User #${log.user_id}` : "Sistema"}</td>
                    <td style={{ fontSize: "0.8rem", color: "var(--color-muted)" }}>{log.ip_address || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
