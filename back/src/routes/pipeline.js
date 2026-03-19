import express from "express";
import { z } from "zod";
import { Document } from "../models/Document.js";

export const pipelineRouter = express.Router();

// Called by Airflow when a document is processed.
// Expected payload (minimal):
// { document_id, status, clean_object_key?, curated_object_key?, contract?, anomalies? }
const doneSchema = z.object({
  document_id: z.string().min(1),
  status: z.enum(["processing", "done", "error"]).optional(),
  clean_object_key: z.string().optional(),
  curated_object_key: z.string().optional(),
  contract: z.record(z.any()).optional(),
  anomalies: z.array(z.string()).optional()
});

pipelineRouter.post("/done", async (req, res) => {
  const parsed = doneSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "invalid_payload" });

  const p = parsed.data;
  const doc = await Document.findOne({ documentId: p.document_id });
  if (!doc) return res.status(404).json({ error: "document_not_found" });

  if (p.status) doc.status = p.status;
  if (p.clean_object_key) doc.cleanObjectKey = p.clean_object_key;
  if (p.curated_object_key) doc.curatedObjectKey = p.curated_object_key;
  if (p.contract) doc.contract = p.contract;
  if (p.anomalies) doc.anomalies = p.anomalies;

  await doc.save();
  return res.json({ ok: true });
});

