import dotenv from "dotenv";

dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || "3001", 10),
  nodeEnv: process.env.NODE_ENV || "development",
  frontendOrigin: process.env.FRONTEND_ORIGIN || "http://localhost:5173",

  mongodbUri: process.env.MONGODB_URI || "mongodb://localhost:27017/hackathon26",
  jwtSecret: process.env.JWT_SECRET || "dev-secret",

  minio: {
    endPoint: process.env.MINIO_ENDPOINT || "localhost",
    port: parseInt(process.env.MINIO_PORT || "9000", 10),
    useSSL: (process.env.MINIO_USE_SSL || "false").toLowerCase() === "true",
    accessKey: process.env.MINIO_ACCESS_KEY || "minioadmin",
    secretKey: process.env.MINIO_SECRET_KEY || "minioadmin",
    bucketRaw: process.env.MINIO_BUCKET_RAW || "raw",
    bucketClean: process.env.MINIO_BUCKET_CLEAN_TEXTS || "clean",
    bucketCurated: process.env.MINIO_BUCKET_CURATED || "curated"
  }
};

