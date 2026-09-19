// pages/IntegrationsPage.jsx — Painel de Automações, Motor de Regras SLA, Webhooks e API Keys
import { useState, useEffect } from "react";
import {
  getRoutingRules,
  createRoutingRule,
  deleteRoutingRule,
  getWebhooks,
  createWebhook,
  deleteWebhook,
  getApiKeys,
  createApiKey,
  revokeApiKey,
  getCategories,
  createCategory,
  deleteCategory,
} from "../api/integrations";

export default function IntegrationsPage() {
  const [activeTab, setActiveTab] = useState("rules");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Regras de Roteamento
  const [rules, setRules] = useState([]);
  const [ruleName, setRuleName] = useState("");
  const [ruleCondition, setRuleCondition] = useState("fraud_risk_gt");
  const [ruleConditionValue, setRuleConditionValue] = useState("0.4");
  const [ruleAction, setRuleAction] = useState("quarantine");

  // Webhooks
  const [webhooks, setWebhooks] = useState([]);
  const [webhookUrl, setWebhookUrl] = useState("");
  const [webhookEvents, setWebhookEvents] = useState("analysis.completed,analysis.sla_alert");

  // API Keys
  const [apiKeys, setApiKeys] = useState([]);
  const [keyName, setKeyName] = useState("");
  const [newlyCreatedKey, setNewlyCreatedKey] = useState(null);

  // Categorias
  const [categories, setCategories] = useState([]);
  const [categoryName, setCategoryName] = useState("");
  const [categoryDesc, setCategoryDesc] = useState("");

  const refreshData = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === "rules") {
        const res = await getRoutingRules();
        setRules(res.data.rules || []);
      } else if (activeTab === "webhooks") {
        const res = await getWebhooks();
        setWebhooks(res.data.subscriptions || []);
      } else if (activeTab === "apikeys") {
        const res = await getApiKeys();
        setApiKeys(res.data.api_keys || []);
      } else if (activeTab === "categories") {
        const res = await getCategories();
        setCategories(res.data.categories || []);
      }
    } catch {
      setError("Não foi possível carregar os dados desta seção.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
    setSuccessMsg(null);
  }, [activeTab]);

  // Handlers para Regras
  const handleCreateRule = async (e) => {
    e.preventDefault();
    if (!ruleName.trim()) return;
    try {
      let condPayload = {};
      if (ruleCondition === "fraud_risk_gt") {
        condPayload = { fraud_risk_gt: parseFloat(ruleConditionValue) };
      } else if (ruleCondition === "urgency_eq") {
        condPayload = { urgency: ruleConditionValue };
      } else if (ruleCondition === "sentiment_eq") {
        condPayload = { sentiment: ruleConditionValue };
      }

      await createRoutingRule({
        name: ruleName.trim(),
        condition: condPayload,
        action: ruleAction,
        action_payload: {},
        priority: 10,
      });

      setRuleName("");
      setSuccessMsg("Regra criada com sucesso!");
      refreshData();
    } catch (err) {
      setError(err.response?.data?.message || "Erro ao criar regra.");
    }
  };

  const handleDeleteRule = async (id) => {
    try {
      await deleteRoutingRule(id);
      refreshData();
    } catch {
      setError("Erro ao excluir regra.");
    }
  };

  // Handlers para Webhooks
  const handleCreateWebhook = async (e) => {
    e.preventDefault();
    if (!webhookUrl.trim()) return;
    try {
      await createWebhook({
        target_url: webhookUrl.trim(),
        events: webhookEvents.split(",").map((s) => s.trim()),
      });
      setWebhookUrl("");
      setSuccessMsg("Webhook registrado com sucesso!");
      refreshData();
    } catch (err) {
      setError(err.response?.data?.message || "Erro ao criar webhook.");
    }
  };

  const handleDeleteWebhook = async (id) => {
    try {
      await deleteWebhook(id);
      refreshData();
    } catch {
      setError("Erro ao remover webhook.");
    }
  };

  // Handlers para API Keys
  const handleCreateApiKey = async (e) => {
    e.preventDefault();
    if (!keyName.trim()) return;
    try {
      const res = await createApiKey(keyName.trim(), 100);
      setNewlyCreatedKey(res.data.raw_key);
      setKeyName("");
      refreshData();
    } catch (err) {
      setError(err.response?.data?.message || "Erro ao gerar chave.");
    }
  };

  const handleRevokeApiKey = async (id) => {
    try {
      await revokeApiKey(id);
      refreshData();
    } catch {
      setError("Erro ao revogar chave.");
    }
  };

  // Handlers para Categorias
  const handleCreateCategory = async (e) => {
    e.preventDefault();
    if (!categoryName.trim()) return;
    try {
      await createCategory({
        name: categoryName.trim(),
        description: categoryDesc.trim(),
        is_productive: true,
      });
      setCategoryName("");
      setCategoryDesc("");
      setSuccessMsg("Categoria criada!");
      refreshData();
    } catch (err) {
      setError(err.response?.data?.message || "Erro ao criar categoria.");
    }
  };

  const handleDeleteCategory = async (id) => {
    try {
      await deleteCategory(id);
      refreshData();
    } catch {
      setError("Erro ao excluir categoria.");
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Automações, Regras & Integrações B2B</h1>
        <p>Configure regras automáticas de SLA, webhooks com assinatura HMAC, API Keys e categorias customizadas.</p>
      </div>

      <div className="tabs-nav">
        <button
          className={`tab-btn ${activeTab === "rules" ? "active" : ""}`}
          onClick={() => setActiveTab("rules")}
        >
          ⚡ Motor de Regras (SLA)
        </button>
        <button
          className={`tab-btn ${activeTab === "webhooks" ? "active" : ""}`}
          onClick={() => setActiveTab("webhooks")}
        >
          🔗 Webhooks Corporativos
        </button>
        <button
          className={`tab-btn ${activeTab === "apikeys" ? "active" : ""}`}
          onClick={() => setActiveTab("apikeys")}
        >
          🔑 Chaves de API (B2B)
        </button>
        <button
          className={`tab-btn ${activeTab === "categories" ? "active" : ""}`}
          onClick={() => setActiveTab("categories")}
        >
          🏷️ Categorias Dinâmicas
        </button>
      </div>

      {successMsg && (
        <div style={{ background: "rgba(63,185,80,0.15)", color: "var(--color-success)", padding: "0.75rem", borderRadius: "var(--radius)", marginBottom: "1rem" }}>
          ✓ {successMsg}
        </div>
      )}
      {error && <div className="error-msg" style={{ marginBottom: "1rem" }}>{error}</div>}

      {/* ABA: REGRAS DE ROTEAMENTO */}
      {activeTab === "rules" && (
        <div>
          <div className="card" style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", marginBottom: "0.75rem" }}>Criar Nova Regra de Automação / SLA</h3>
            <form onSubmit={handleCreateRule}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
                <div className="form-group">
                  <label>Nome da Regra</label>
                  <input
                    type="text"
                    placeholder="Ex: Quarentena de Alto Risco"
                    value={ruleName}
                    onChange={(e) => setRuleName(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Quando (Condição)</label>
                  <select
                    value={ruleCondition}
                    onChange={(e) => {
                      setRuleCondition(e.target.value);
                      if (e.target.value === "urgency_eq") setRuleConditionValue("Critica");
                      else if (e.target.value === "sentiment_eq") setRuleConditionValue("Irritado");
                      else setRuleConditionValue("0.4");
                    }}
                  >
                    <option value="fraud_risk_gt">Risco de Fraude &gt; X</option>
                    <option value="urgency_eq">Urgência Igual a</option>
                    <option value="sentiment_eq">Sentimento Igual a</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Valor da Condição</label>
                  {ruleCondition === "fraud_risk_gt" ? (
                    <input
                      type="number"
                      step="0.1"
                      min="0.1"
                      max="1.0"
                      value={ruleConditionValue}
                      onChange={(e) => setRuleConditionValue(e.target.value)}
                    />
                  ) : ruleCondition === "urgency_eq" ? (
                    <select
                      value={ruleConditionValue}
                      onChange={(e) => setRuleConditionValue(e.target.value)}
                    >
                      <option value="Critica">Crítica</option>
                      <option value="Alta">Alta</option>
                      <option value="Media">Média</option>
                    </select>
                  ) : (
                    <select
                      value={ruleConditionValue}
                      onChange={(e) => setRuleConditionValue(e.target.value)}
                    >
                      <option value="Irritado">Irritado</option>
                      <option value="Negativo">Negativo</option>
                    </select>
                  )}
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", alignItems: "flex-end" }}>
                <div className="form-group">
                  <label>Ação Automática</label>
                  <select value={ruleAction} onChange={(e) => setRuleAction(e.target.value)}>
                    <option value="quarantine">Mover para Quarentena Humana</option>
                    <option value="set_urgency">Elevar Urgência para Crítica</option>
                    <option value="alert_webhook">Disparar Webhook de Alerta SLA</option>
                  </select>
                </div>
                <button className="btn-primary" style={{ height: "42px" }}>
                  Adicionar Regra
                </button>
              </div>
            </form>
          </div>

          <div className="card">
            <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Regras Ativas do Tenant</h3>
            {loading ? (
              <div className="spinner" />
            ) : rules.length === 0 ? (
              <p style={{ color: "var(--color-muted)" }}>Nenhuma regra configurada ainda.</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Condição</th>
                    <th>Ação</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {rules.map((r) => (
                    <tr key={r.id}>
                      <td><strong>{r.name}</strong></td>
                      <td><code>{JSON.stringify(r.condition)}</code></td>
                      <td><span className="badge" style={{ background: "rgba(88,166,255,0.15)", color: "var(--color-primary)" }}>{r.action}</span></td>
                      <td>
                        <button
                          className="btn-danger"
                          style={{ padding: "0.2rem 0.6rem", fontSize: "0.75rem" }}
                          onClick={() => handleDeleteRule(r.id)}
                        >
                          Excluir
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* ABA: WEBHOOKS */}
      {activeTab === "webhooks" && (
        <div>
          <div className="card" style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", marginBottom: "0.75rem" }}>Cadastrar Novo Endpoint Webhook</h3>
            <form onSubmit={handleCreateWebhook}>
              <div className="form-group">
                <label>URL de Destino (HTTPS)</label>
                <input
                  type="url"
                  placeholder="https://api.suaempresa.com/webhooks/autou"
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Eventos Assinados (separados por vírgula ou *)</label>
                <input
                  type="text"
                  value={webhookEvents}
                  onChange={(e) => setWebhookEvents(e.target.value)}
                />
              </div>
              <button className="btn-primary">Registrar Webhook</button>
            </form>
          </div>

          <div className="card">
            <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Webhooks Cadastrados</h3>
            {webhooks.length === 0 ? (
              <p style={{ color: "var(--color-muted)" }}>Nenhum webhook registrado.</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>URL</th>
                    <th>Eventos</th>
                    <th>Secret HMAC</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {webhooks.map((w) => (
                    <tr key={w.id}>
                      <td style={{ maxWidth: "250px", overflow: "hidden", textOverflow: "ellipsis" }}>{w.target_url}</td>
                      <td>{w.events?.join(", ") || "*"}</td>
                      <td><code style={{ fontSize: "0.75rem" }}>{w.secret}</code></td>
                      <td>
                        <button
                          className="btn-danger"
                          style={{ padding: "0.2rem 0.6rem", fontSize: "0.75rem" }}
                          onClick={() => handleDeleteWebhook(w.id)}
                        >
                          Remover
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* ABA: API KEYS */}
      {activeTab === "apikeys" && (
        <div>
          {newlyCreatedKey && (
            <div style={{ background: "rgba(63,185,80,0.15)", border: "1px solid var(--color-success)", padding: "1rem", borderRadius: "var(--radius)", marginBottom: "1.5rem" }}>
              <strong>🔑 Sua Nova API Key B2B:</strong>
              <p style={{ fontSize: "0.85rem", margin: "0.5rem 0", color: "var(--color-muted)" }}>
                Copie agora. Por motivos de segurança ela não será exibida novamente:
              </p>
              <code style={{ background: "#000", padding: "0.4rem 0.8rem", borderRadius: "4px", display: "block", wordBreak: "break-all" }}>
                {newlyCreatedKey}
              </code>
            </div>
          )}

          <div className="card" style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", marginBottom: "0.75rem" }}>Gerar Nova API Key de Integração</h3>
            <form onSubmit={handleCreateApiKey} style={{ display: "flex", gap: "1rem", alignItems: "flex-end" }}>
              <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
                <label>Identificador da Chave (ex: Produção CRM / Backend On-premise)</label>
                <input
                  type="text"
                  placeholder="CRM Backend"
                  value={keyName}
                  onChange={(e) => setKeyName(e.target.value)}
                />
              </div>
              <button className="btn-primary" style={{ height: "42px" }}>Gerar Chave</button>
            </form>
          </div>

          <div className="card">
            <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Chaves de API Ativas</h3>
            {apiKeys.length === 0 ? (
              <p style={{ color: "var(--color-muted)" }}>Nenhuma chave de API gerada.</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Prefixo</th>
                    <th>Rate Limit</th>
                    <th>Criado em</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {apiKeys.map((k) => (
                    <tr key={k.id}>
                      <td><strong>{k.name}</strong></td>
                      <td><code>{k.key_prefix}...</code></td>
                      <td>{k.rate_limit_per_minute} req/min</td>
                      <td>{new Date(k.created_at).toLocaleDateString("pt-BR")}</td>
                      <td>
                        <button
                          className="btn-danger"
                          style={{ padding: "0.2rem 0.6rem", fontSize: "0.75rem" }}
                          onClick={() => handleRevokeApiKey(k.id)}
                        >
                          Revogar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* ABA: CATEGORIAS DINÂMICAS */}
      {activeTab === "categories" && (
        <div>
          <div className="card" style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", marginBottom: "0.75rem" }}>Adicionar Categoria Dinâmica para o Tenant</h3>
            <form onSubmit={handleCreateCategory}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr auto", gap: "1rem", alignItems: "flex-end" }}>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label>Nome da Categoria</label>
                  <input
                    type="text"
                    placeholder="Ex: Suporte Nível 2"
                    value={categoryName}
                    onChange={(e) => setCategoryName(e.target.value)}
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label>Descrição / Critério Semântico para IA</label>
                  <input
                    type="text"
                    placeholder="Dúvidas técnicas e chamados de erros no sistema..."
                    value={categoryDesc}
                    onChange={(e) => setCategoryDesc(e.target.value)}
                  />
                </div>
                <button className="btn-primary" style={{ height: "42px" }}>Salvar Categoria</button>
              </div>
            </form>
          </div>

          <div className="card">
            <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Categorias Cadastradas</h3>
            {categories.length === 0 ? (
              <p style={{ color: "var(--color-muted)" }}>Utilizando categorias padrão do sistema (Produtivo / Improdutivo).</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Descrição</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {categories.map((c) => (
                    <tr key={c.id}>
                      <td><strong>{c.name}</strong></td>
                      <td>{c.description || "—"}</td>
                      <td>
                        <button
                          className="btn-danger"
                          style={{ padding: "0.2rem 0.6rem", fontSize: "0.75rem" }}
                          onClick={() => handleDeleteCategory(c.id)}
                        >
                          Excluir
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
