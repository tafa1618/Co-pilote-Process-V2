import type { User } from "../types";

export interface ProductivityPayload {
  preview?: Record<string, unknown>[];
  global?: {
    total_hours: number;
    total_facturable: number;
    productivite: number;
  };
  monthly: { mois: string; productivite: number }[];
  teams: { ["Salarié - Equipe(Nom)"]: string; productivite: number }[];
  technicians: { ["Salarié - Nom"]: string; productivite: number }[];
  heatmap: { mois: string; ["Salarié - Equipe(Nom)"]: string; productivite: number; delta_vs_month: number }[];
  correlation?: { equipe: string; score: number } | null;
  exhaustivity?: {
    periods: string[];
    per_period: {
      [period: string]: {
        statuts: Record<string, Record<string, string>>;
        heures: Record<string, Record<string, number>>;
        teams: Record<string, string>;
      };
    };
  } | null;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";
const DEFAULT_EMAIL = (import.meta.env.VITE_ADMIN_EMAIL || "admin@neemba.com").trim().toLowerCase();

export async function fetchProductivity(user: User | null): Promise<ProductivityPayload> {
  const email = (user?.email || DEFAULT_EMAIL).trim().toLowerCase();
  const res = await fetch(`${BACKEND_URL}/kpi/productivite/analytics`, {
    headers: {
      "X-User-Email": email,
      ...(user?.adminPassword ? { "X-Admin-Password": user.adminPassword } : {}),
    },
  });
  if (!res.ok) {
    throw new Error("Impossible de charger les KPI de productivité");
  }
  return res.json();
}

