import express from "express";
import { z } from "zod";
import { Document } from "../models/Document.js";
import { Supplier } from "../models/Supplier.js";

export const pipelineRouter = express.Router();

const doneSchema = z.object({
  document_id: z.string().min(1),
  status: z.enum(["processing", "done", "error"]).optional(),
  clean_object_key: z.string().optional(),
  curated_object_key: z.string().optional(),
  ocr_confidence: z.number().optional(),
  contract: z.record(z.any()).optional(),
  anomalies: z.array(z.string()).optional()
});

pipelineRouter.post("/done", async (req, res) => {
  const parsed = doneSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "invalid_payload" });

  const p = parsed.data;
  
  let doc = await Document.findOne({ documentId: p.document_id });
  if (!doc) {
    doc = new Document({
      documentId: p.document_id,
      filename: p.document_id,
      documentType: "facture_fournisseur",
      status: "uploaded",
    });
  }

  if (p.status) doc.status = p.status;
  if (p.clean_object_key) doc.cleanObjectKey = p.clean_object_key;
  if (p.curated_object_key) doc.curatedObjectKey = p.curated_object_key;
  if (p.contract) doc.contract = p.contract;
  if (p.anomalies) doc.anomalies = p.anomalies;
  if (p.ocr_confidence) doc.ocrConfidence = p.ocr_confidence;

  const siret = p.contract?.siret;
  if (siret) {
    let supplier = await Supplier.findOne({ siret });
    if (!supplier) {
      supplier = await Supplier.create({
        companyName: p.contract?.raison_sociale || `Fournisseur ${siret}`,
        siret,
        contactEmail: p.contract?.emails?.[0] || "",
        rib: p.contract?.ibans?.[0] || "",
      });
    }
    doc.supplierId = supplier._id;
  }

  await doc.save();
  return res.json({ ok: true });
});

