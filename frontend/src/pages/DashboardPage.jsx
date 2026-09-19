// pages/DashboardPage.jsx — Métricas de ROI, acurácia, quarentena e distribuição semântica
import { useEffect, useState } from "react";
import { getStats } from "../api/stats";

function StatCard({ value, label, color, subtitle }) {
  return (
    <div className="stat-card">
      <div className="stat-value" style={color ? { color } : {}}>
        {value ?? "—"}
      </div>
      <div className="stat-label">{label}</div>
      {subtitle && (
        <span style={{ fontSize: "0.72rem", color: "var(--color-muted)", marginTop: "0.2rem" }}>
          {subtitle}
        </span>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getStats()
      .then((res) => setStats(res.data))
      .catch(() => setError("Não foi possível carregar as métricas."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Painel de ROI & Performance B2B</h1>
        <p>Métricas operacionais agregadas, mensuração de ROI financeiro e acurácia dos modelos.</p>
      </div>

      {loading && <div className="spinner" />}
      {error && <div className="error-msg">{error}</div>}

      {stats && (
        <>
          {/* Banner de ROI Financeiro */}
          <div className="roi-banner">
            <div>
              <h2 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "0.25rem" }}>
                💼 Retorno sobre Investimento (ROI Estimado)
              </h2>
              <p style={{ color: "var(--color-muted)", fontSize: "0.85rem" }}>
                Baseado no tempo economizado de triagem manual humana por analista (R$ 45,00/h).
              </p>
            </div>
            <div className="roi-stats">
              <div className="roi-item">
                <h3>{stats.time_saved_estimate_hours || 0} hrs</h3>
                <p>Horas Humanas Salvas</p>
              </div>
              <div className="roi-item">
                <h3>
                  R${" "}
                  {Number(stats.financial_saved_estimate_brl || 0).toLocaleString("pt-BR", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </h3>
                <p>Valor Financeiro Economizado</p>
              </div>
            </div>
          </div>

          {/* Grid Principal de KPIs */}
          <div className="stats-grid">
            <StatCard
              value={stats.total_analyses}
              label="Volume Total de E-mails"
              subtitle="Análises processadas"
            />
            <StatCard
              value={`${stats.productive_count} (${stats.productive_percentage}%)`}
              label="E-mails Produtivos"
              color="var(--color-success)"
              subtitle="Requerem ação do time"
            />
            <StatCard
              value={`${stats.unproductive_count} (${stats.unproductive_percentage}%)`}
              label="E-mails Improdutivos"
              color="var(--color-danger)"
              subtitle="Descartáveis / Informativos"
            />
            <StatCard
              value={`${stats.avg_processing_time_ms} ms`}
              label="Tempo Médio de Resposta"
              subtitle="Latência do motor"
            />
            <StatCard
              value={`${stats.quarantine_rate || "0.0"}%`}
              label="Taxa de Quarentena"
              color="var(--color-warning)"
              subtitle={`${stats.quarantine_count || 0} e-mails retidos`}
            />
            <StatCard
              value={stats.cached_count}
              label="Economia via Cache"
              color="var(--color-primary)"
              subtitle="Respostas instantâneas"
            />
            <StatCard
              value={stats.total_feedbacks}
              label="Feedbacks Recebidos"
              subtitle="Human-in-the-loop"
            />
            <StatCard
              value={stats.corrections_count}
              label="Ajustes por Operadores"
              color="var(--color-warning)"
              subtitle="Refinamento contínuo"
            />
          </div>

          {/* Quebras por Urgência e Sentimento */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginTop: "1rem" }}>
            <div className="card">
              <h3 style={{ fontSize: "1rem", marginBottom: "1rem", color: "var(--color-muted)", textTransform: "uppercase" }}>
                Distribuição por Urgência
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>🚨 Crítica</span>
                  <strong>{stats.urgency_breakdown?.Critica || 0}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>⚡ Alta</span>
                  <strong>{stats.urgency_breakdown?.Alta || 0}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>🔹 Média</span>
                  <strong>{stats.urgency_breakdown?.Media || 0}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>🟢 Baixa</span>
                  <strong>{stats.urgency_breakdown?.Baixa || 0}</strong>
                </div>
              </div>
            </div>

            <div className="card">
              <h3 style={{ fontSize: "1rem", marginBottom: "1rem", color: "var(--color-muted)", textTransform: "uppercase" }}>
                Distribuição de Sentimento
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>😊 Positivo</span>
                  <strong>{stats.sentiment_breakdown?.Positivo || 0}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>😐 Neutro</span>
                  <strong>{stats.sentiment_breakdown?.Neutro || 0}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>😟 Negativo</span>
                  <strong>{stats.sentiment_breakdown?.Negativo || 0}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>😡 Irritado</span>
                  <strong style={{ color: "var(--color-danger)" }}>
                    {stats.sentiment_breakdown?.Irritado || 0}
                  </strong>
                </div>
              </div>
            </div>
          </div>

          {stats.total_analyses === 0 && (
            <div className="card" style={{ textAlign: "center", color: "var(--color-muted)", marginTop: "1.5rem" }}>
              Nenhuma análise processada ainda. <a href="/">Analise um e-mail</a> para gerar métricas.
            </div>
          )}
        </>
      )}
    </div>
  );
}
