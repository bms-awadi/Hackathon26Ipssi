import mongoose from "mongoose";

const userSchema = new mongoose.Schema(
  {
    email: { type: String, required: true, unique: true, index: true },
    passwordHash: { type: String, required: true },
    role: {
      type: String,
      enum: ["operator", "supplier", "admin"],
      default: "operator"
    }
  },
  { timestamps: true }
);

export const User = mongoose.model("User", userSchema);

