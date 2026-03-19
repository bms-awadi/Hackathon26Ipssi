const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3001";

function getHeaders(json = true) {
  const h = {};
  const token = localStorage.getItem("token");
  if (token) h["Authorization"] = `Bearer ${token}`;
  if (json) h["Content-Type"] = "application/json";
  return h;
}

export async function login(email, password) {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export async function register(email, password, role) {
  const res = await fetch(`${API_URL}/api/auth/register`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ email, password, role }),
  });
  return res.json();
}

export async function fetchSuppliers() {
  const res = await fetch(`${API_URL}/api/suppliers`, { headers: getHeaders() });
  const data = await res.json();
  return data.suppliers || [];
}

export async function fetchSupplier(id) {
  const res = await fetch(`${API_URL}/api/suppliers/${id}`, { headers: getHeaders() });
  return res.json();
}

export async function fetchDocuments() {
  const res = await fetch(`${API_URL}/api/documents`, { headers: getHeaders() });
  const data = await res.json();
  return data.documents || [];
}

export async function uploadDocuments(files) {
  const formData = new FormData();
  for (const file of files) formData.append("files", file);
  const res = await fetch(`${API_URL}/api/documents/upload`, {
    method: "POST",
    headers: getHeaders(false),
    body: formData,
  });
  return res.json();
}

// operator → /operator, supplier → /crm, admin → /compliance
export function getRoleRoute(role) {
  return { operator: "/operator", supplier: "/crm", admin: "/compliance" }[role] || "/";
}

export function getRoleLabel(role) {
  return { operator: "Opérateur", supplier: "Comptable / CRM", admin: "Conformité" }[role] || role;
}
