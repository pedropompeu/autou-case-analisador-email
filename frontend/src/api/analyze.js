// api/analyze.js — Chamadas completas de análise de email, workflow e notas
import client from "./client";

/**
 * Analisa um email pelo conteúdo com tom e contexto opcionais.
 */
export const analyzeEmail = (
  emailContent,
  senderEmail = null,
  subject = null,
  tone = "formal",
  useThreadContext = true,
  saveHistory = true
) =>
  client.post("/analyze", {
    email_content: emailContent,
    sender_email: senderEmail,
    subject,
    tone,
    use_thread_context: useThreadContext,
    save_history: saveHistory,
  });

/**
 * Regenera a sugestão de resposta mudando o tom.
 */
export const regenerateTone = (analysisId, tone) =>
  client.post("/analyze/regenerate-tone", {
    analysis_id: analysisId,
    tone,
  });

/**
 * Analisa email com arquivo anexo (PDF, TXT ou EML).
 */
export const analyzeWithFile = (formData) =>
  client.post("/analyze-with-file", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

/**
 * Ingestão nativa de arquivo EML / RFC822.
 */
export const ingestEml = (formData) =>
  client.post("/ingest/eml", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

/**
 * Busca o status de uma tarefa assíncrona.
 */
export const getTaskStatus = (taskId) => client.get(`/tasks/${taskId}`);

/**
 * Notas internas na thread do email.
 */
export const getNotes = (analysisId) => client.get(`/emails/${analysisId}/notes`);

export const addNote = (analysisId, content) =>
  client.post(`/emails/${analysisId}/notes`, { content });

/**
 * Atualização de status e atribuição do chamado.
 */
export const updateAnalysisStatus = (analysisId, status) =>
  client.patch(`/emails/${analysisId}/status`, { status });

export const assignOperator = (analysisId, userId) =>
  client.patch(`/emails/${analysisId}/assign`, { assigned_to_user_id: userId });
