import { Client as MinioClient } from "minio";
import { config } from "./config.js";

export const minio = new MinioClient({
  endPoint: config.minio.endPoint,
  port: config.minio.port,
  useSSL: config.minio.useSSL,
  accessKey: config.minio.accessKey,
  secretKey: config.minio.secretKey
});

export async function ensureBuckets() {
  const buckets = [
    config.minio.bucketRaw,
    config.minio.bucketClean,
    config.minio.bucketCurated
  ];
  for (const b of buckets) {
    // eslint-disable-next-line no-await-in-loop
    const exists = await minio.bucketExists(b).catch(() => false);
    if (!exists) {
      // eslint-disable-next-line no-await-in-loop
      await minio.makeBucket(b, "eu-west-1").catch(() => {});
    }
  }
}

export async function getJson(bucket, objectKey) {
  const stream = await minio.getObject(bucket, objectKey);
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  const buf = Buffer.concat(chunks);
  return JSON.parse(buf.toString("utf-8"));
}

