import mongoose from "mongoose";

const supplierSchema = new mongoose.Schema(
  {
    companyName: { type: String, required: true },
    siret: { type: String, index: true },
    contactEmail: { type: String },
    rib: { type: String }
  },
  { timestamps: true }
);

export const Supplier = mongoose.model("Supplier", supplierSchema);

