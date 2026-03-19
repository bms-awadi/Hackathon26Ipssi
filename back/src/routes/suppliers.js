import express from "express";
import { z } from "zod";
import { requireAuth } from "../auth.js";
import { Supplier } from "../models/Supplier.js";
import { Document } from "../models/Document.js";

export const suppliersRouter = express.Router();

suppliersRouter.get("/", requireAuth, async (_req, res) => {
  const suppliers = await Supplier.find().sort({ createdAt: -1 }).limit(200);
  return res.json({ suppliers });
});

const createSchema = z.object({
  companyName: z.string().min(1),
  siret: z.string().optional(),
  contactEmail: z.string().email().optional(),
  rib: z.string().optional()
});

suppliersRouter.post("/", requireAuth, async (req, res) => {
  const parsed = createSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "invalid_payload" });
  const supplier = await Supplier.create(parsed.data);
  return res.json({ supplier });
});

suppliersRouter.get("/:id", requireAuth, async (req, res) => {
  const supplier = await Supplier.findById(req.params.id);
  if (!supplier) return res.status(404).json({ error: "not_found" });
  const documents = await Document.find({ supplierId: supplier._id })
    .sort({ createdAt: -1 })
    .limit(200);
  return res.json({ supplier, documents });
});

