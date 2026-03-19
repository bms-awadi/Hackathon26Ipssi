import jwt from "jsonwebtoken";
import { config } from "./config.js";

export function signToken(user) {
  return jwt.sign(
    { sub: String(user._id), email: user.email, role: user.role },
    config.jwtSecret,
    { expiresIn: "7d" }
  );
}

export function requireAuth(req, res, next) {
  const h = req.headers.authorization || "";
  const [kind, token] = h.split(" ");
  if (kind !== "Bearer" || !token) return res.status(401).json({ error: "unauthorized" });
  try {
    req.user = jwt.verify(token, config.jwtSecret);
    return next();
  } catch {
    return res.status(401).json({ error: "unauthorized" });
  }
}

export function requireRole(roles) {
  return (req, res, next) => {
    const role = req.user?.role;
    if (!role || !roles.includes(role)) return res.status(403).json({ error: "forbidden" });
    return next();
  };
}

