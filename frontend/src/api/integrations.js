// api/integrations.js — Webhooks, API Keys, Routing Rules, Categorias e LGPD
import client from "./client";

// --- Webhooks ---
export const getWebhooks = () => client.get("/webhooks");
export const createWebhook = (data) => client.post("/webhooks", data);
export const deleteWebhook = (id) => client.delete(`/webhooks/${id}`);

// --- B2B API Keys ---
export const getApiKeys = () => client.get("/admin/api-keys");
export const createApiKey = (name, rateLimit = 100) =>
  client.post("/admin/api-keys", { name, rate_limit_per_minute: rateLimit });
export const revokeApiKey = (id) => client.delete(`/admin/api-keys/${id}`);

// --- Motor de Regras & SLA ---
export const getRoutingRules = () => client.get("/routing-rules");
export const createRoutingRule = (data) => client.post("/routing-rules", data);
export const deleteRoutingRule = (id) => client.delete(`/routing-rules/${id}`);

// --- Categorias Customizadas ---
export const getCategories = () => client.get("/categories");
export const createCategory = (data) => client.post("/categories", data);
export const deleteCategory = (id) => client.delete(`/categories/${id}`);

// --- Compliance & LGPD ---
export const exportSubjectData = (identifier) =>
  client.post("/compliance/export", { subject_identifier: identifier });

export const eraseSubjectData = (identifier) =>
  client.post("/compliance/erase", { subject_identifier: identifier });

// --- Trilha de Auditoria ---
export const getAuditLogs = (limit = 50) =>
  client.get(`/admin/audit-logs?limit=${limit}`);
