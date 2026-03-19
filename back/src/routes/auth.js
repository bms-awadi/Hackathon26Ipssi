import express from "express";
import bcrypt from "bcryptjs";
import { z } from "zod";
import { User } from "../models/User.js";
import { signToken } from "../auth.js";

export const authRouter = express.Router();

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
  role: z.enum(["operator", "supplier", "admin"]).optional()
});

authRouter.post("/register", async (req, res) => {
  const parsed = registerSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "invalid_payload" });

  const { email, password, role } = parsed.data;
  const existing = await User.findOne({ email });
  if (existing) return res.status(409).json({ error: "email_taken" });

  const passwordHash = await bcrypt.hash(password, 10);
  const user = await User.create({ email, passwordHash, role: role || "operator" });
  const token = signToken(user);
  return res.json({ token, user: { email: user.email, role: user.role } });
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1)
});

authRouter.post("/login", async (req, res) => {
  const parsed = loginSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "invalid_payload" });

  const { email, password } = parsed.data;
  const user = await User.findOne({ email });
  if (!user) return res.status(401).json({ error: "invalid_credentials" });

  const ok = await bcrypt.compare(password, user.passwordHash);
  if (!ok) return res.status(401).json({ error: "invalid_credentials" });

  const token = signToken(user);
  return res.json({ token, user: { email: user.email, role: user.role } });
});

