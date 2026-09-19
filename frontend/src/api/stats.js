// api/stats.js — Dashboard e feedback
import client from "./client";

export const getStats = () => client.get("/stats");

export const submitFeedback = (analysisId, approved, correctedCategory = null, notes = null) =>
  client.post("/feedback", {
    analysis_id: analysisId,
    approved,
    corrected_category: correctedCategory,
    notes,
  });
