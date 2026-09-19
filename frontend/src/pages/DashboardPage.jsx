// pages/DashboardPage.jsx — Métricas agregadas
import { useEffect, useState } from "react";
import { getStats } from "../api/stats";

function StatCard({ value, label, color }) {
  return (
    <div className="stat-card">
      <div className="stat-value" style={color ? { color } : {}}>
        {value ?? "—"}
      </div>
      <div className="stat-label">{label}</div>
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
        <h1>Dashboard</h1>
        <p>Métricas agregadas de análises e feedback.</p>
      </div>

      {loading && <div className="spinner" />}
      {error && <div className="error-msg">{error}</div>}

      {stats && (
        <>
          <div className="stats-grid">
            <StatCard value={stats.total_analyses} label="Total de análises" />
            <StatCard
              value={`${stats.productive_count} (${stats.productive_percentage}%)`}
              label="Produtivos"
              color="var(--color-success)"
            />
            <StatCard
              value={`${stats.unproductive_count} (${stats.unproductive_percentage}%)`}
              label="Improdutivos"
              color="var(--color-danger)"
            />
            <StatCard value={`${stats.avg_processing_time_ms} ms`} label="Tempo médio de análise" />
            <StatCard value={stats.cached_count} label="Servidos do cache" />
            <StatCard value={stats.total_feedbacks} label="Feedbacks recebidos" />
            <StatCard
              value={stats.corrections_count}
              label="Correções enviadas"
              color="var(--color-warning)"
            />
            <StatCard
              value={`${stats.time_saved_estimate_hours} h`}
              label="Tempo estimado economizado"
              color="var(--color-primary)"
            />
          </div>

          {stats.total_analyses === 0 && (
            <div className="card" style={{ textAlign: "center", color: "var(--color-muted)" }}>
              Nenhuma análise ainda. <a href="/">Analise um e-mail</a> para começar.
            </div>
          )}
        </>
      )}
    </div>
  );
}
