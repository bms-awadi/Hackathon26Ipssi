import express from "express";
import multer from "multer";
import { z } from "zod";
import { randomUUID } from "crypto";

import { requireAuth } from "../auth.js";
import { Document } from "../models/Document.js";
import { Supplier } from "../models/Supplier.js";
import { config } from "../config.js";
import { minio, getJson } from "../minio.js";

export const documentsRouter = express.Router();

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 25 * 1024 * 1024 } // 25MB each
});

const uploadSchema = z.object({
  supplierId: z.string().optional(),
  documentType: z.string().optional()
});

documentsRouter.post(
  "/upload",
  requireAuth,
  upload.array("files", 20),
  async (req, res) => {
    const parsed = uploadSchema.safeParse(req.body || {});
    if (!parsed.success) return res.status(400).json({ error: "invalid_payload" });

    const files = req.files || [];
    if (!Array.isArray(files) || files.length === 0) {
      return res.status(400).json({ error: "no_files" });
    }

    let supplier = null;
    if (parsed.data.supplierId) {
      supplier = await Supplier.findById(parsed.data.supplierId);
      if (!supplier) return res.status(404).json({ error: "supplier_not_found" });
    }

    const created = [];

    for (const f of files) {
      const documentId = randomUUID();
      const ext = (f.originalname || "").split(".").pop();
      const safeExt = ext && ext.length <= 8 ? `.${ext.toLowerCase()}` : "";
      const objectKey = `${documentId}${safeExt}`;

      // upload to MinIO raw bucket
      // eslint-disable-next-line no-await-in-loop
      await minio.putObject(
        config.minio.bucketRaw,
        objectKey,
        f.buffer,
        f.size,
        { "Content-Type": f.mimetype || "application/octet-stream" }
      );

      // create DB record
      // eslint-disable-next-line no-await-in-loop
      const doc = await Document.create({
        documentId,
        supplierId: supplier?._id,
        filename: f.originalname,
        mimeType: f.mimetype,
        sizeBytes: f.size,
        documentType: parsed.data.documentType || "unknown",
        status: "uploaded",
        rawObjectKey: objectKey
      });

      created.push({
        documentId: doc.documentId,
        status: doc.status,
        rawObjectKey: doc.rawObjectKey
      });
    }

    return res.json({ documents: created });
  }
);

documentsRouter.get("/", requireAuth, async (_req, res) => {
  const docs = await Document.find().sort({ createdAt: -1 }).limit(200);
  return res.json({ documents: docs });
});

documentsRouter.get("/:documentId", requireAuth, async (req, res) => {
  const doc = await Document.findOne({ documentId: req.params.documentId });
  if (!doc) return res.status(404).json({ error: "not_found" });
  return res.json({ document: doc });
});

documentsRouter.get("/:documentId/clean", requireAuth, async (req, res) => {
  const documentId = req.params.documentId;
  const objectKey = `${documentId}.json`;
  try {
    const json = await getJson(config.minio.bucketClean, objectKey);
    return res.json(json);
  } catch {
    return res.status(404).json({ error: "clean_not_found" });
  }
});

documentsRouter.get("/:documentId/curated", requireAuth, async (req, res) => {
  const documentId = req.params.documentId;
  // if we stored curatedObjectKey, use it; otherwise try a common pattern
  const doc = await Document.findOne({ documentId });
  const key = doc?.curatedObjectKey || `curated_${documentId}.json`;
  try {
    const json = await getJson(config.minio.bucketCurated, key);
    return res.json(json);
  } catch {
    return res.status(404).json({ error: "curated_not_found" });
  }
});

