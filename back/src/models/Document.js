import mongoose from "mongoose";

const documentSchema = new mongoose.Schema(
  {
    documentId: { type: String, required: true, unique: true, index: true },
    supplierId: { type: mongoose.Schema.Types.ObjectId, ref: "Supplier" },

    filename: { type: String, required: true },
    mimeType: { type: String },
    sizeBytes: { type: Number },
    documentType: { type: String, default: "unknown" },

    status: {
      type: String,
      enum: ["uploaded", "processing", "done", "error"],
      default: "uploaded"
    },

    // MinIO object keys
    rawObjectKey: { type: String },
    cleanObjectKey: { type: String },
    curatedObjectKey: { type: String },

    // last pipeline output (optional cache)
    contract: { type: Object },
    anomalies: { type: [String], default: [] },
    ocrConfidence: { type: Number }
  },
  { timestamps: true }
);

export const Document = mongoose.model("Document", documentSchema);

