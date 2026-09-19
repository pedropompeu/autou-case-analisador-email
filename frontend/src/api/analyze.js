// api/analyze.js — Chamadas de análise de email
import client from "./client";

/**
 * Analisa um email pelo conteúdo (texto).
 * @param {string} emailContent - Conteúdo do email
 * @param {string} [senderEmail] - Remetente (opcional)
 * @param {string} [subject] - Assunto (opcional)
 */
export const analyzeEmail = (emailContent, senderEmail = null, subject = null) =>
  client.post("/analyze", { email_content: emailContent, sender_email: senderEmail, subject });

/**
 * Analisa email com arquivo anexo (PDF ou TXT).
 */
export const analyzeWithFile = (formData) =>
  client.post("/analyze-with-file", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

/**
 * Busca o status de uma tarefa assíncrona.
 */
export const getTaskStatus = (taskId) => client.get(`/tasks/${taskId}`);
