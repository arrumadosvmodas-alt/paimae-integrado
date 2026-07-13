export type ApiError = {
  detail?: string;
};

const API_URL = import.meta.env.VITE_API_URL ?? "";

export function getToken(): string | null {
  return localStorage.getItem("paimae.token");
}

export function setToken(token: string | null): void {
  if (token) {
    localStorage.setItem("paimae.token", token);
  } else {
    localStorage.removeItem("paimae.token");
  }
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const data = (await response.json().catch(() => ({}))) as any;
    let errorMessage = `Erro HTTP ${response.status}`;
    if (data.detail) {
      if (typeof data.detail === "string") {
        errorMessage = data.detail;
      } else if (Array.isArray(data.detail)) {
        errorMessage = data.detail.map((err: any) => `${err.loc?.join(".") || "Erro"}: ${err.msg}`).join(" | ");
      } else if (typeof data.detail === "object" && data.detail.message) {
        errorMessage = data.detail.message;
      } else {
        errorMessage = JSON.stringify(data.detail);
      }
    }
    throw new Error(errorMessage);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function login(email: string, password: string): Promise<string> {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form
  });
  if (!response.ok) {
    throw new Error("E-mail ou senha invalidos.");
  }
  const data = (await response.json()) as { access_token: string };
  setToken(data.access_token);
  return data.access_token;
}

