import express from "express";
import cors from "cors";
import { config } from "./config.js";
import { connectDb } from "./db.js";
import { ensureBuckets } from "./minio.js";

import { authRouter } from "./routes/auth.js";
import { documentsRouter } from "./routes/documents.js";
import { suppliersRouter } from "./routes/suppliers.js";
import { pipelineRouter } from "./routes/pipeline.js";

const app = express();

app.use(
  cors({
    origin: config.frontendOrigin,
    credentials: true
  })
);
app.use(express.json({ limit: "2mb" }));

app.get("/health", (_req, res) => res.json({ ok: true }));

app.use("/api/auth", authRouter);
app.use("/api/documents", documentsRouter);
app.use("/api/suppliers", suppliersRouter);
app.use("/api/pipeline", pipelineRouter);

app.use((err, _req, res, _next) => {
  // eslint-disable-next-line no-console
  console.error(err);
  res.status(500).json({ error: "internal_error" });
});

await connectDb();
await ensureBuckets();

app.listen(config.port, () => {
  // eslint-disable-next-line no-console
  console.log(`[backend] listening on :${config.port}`);
});

