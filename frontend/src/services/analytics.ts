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

export interface ExhaustivityPayload {
  periods: string[];
  statuts: Record<string, Record<string, string>>;
  heures: Record<string, Record<string, number>>;
  teams: Record<string, string>;
}

export async function fetchExhaustivity(params: { month?: string; team?: string; email?: string; adminPassword?: string }) {
  const email = (params.email || DEFAULT_EMAIL).trim().toLowerCase();
  const search = new URLSearchParams();
  if (params.month) search.set("month", params.month);
  if (params.team) search.set("team", params.team);

  const res = await fetch(`${BACKEND_URL}/kpi/productivite/exhaustivite?${search.toString()}`, {
    headers: {
      "X-User-Email": email,
      ...(params.adminPassword ? { "X-Admin-Password": params.adminPassword } : {}),
    },
  });

  if (!res.ok) {
    throw new Error("Impossible de charger l'exhaustivité");
  }

  return (await res.json()) as ExhaustivityPayload;
}

export interface InspectionAnalyticsPayload {
  period: string;
  start_date: string;
  end_date: string;
  total: number; // Nombre total d'OR uniques facturés
  inspected: number; // Nombre d'OR inspectés
  not_inspected: number; // Nombre d'OR non inspectés
  total_lines?: number; // Nombre total de lignes (pour référence)
  inspected_lines?: number; // Nombre de lignes inspectées (pour référence)
  not_inspected_lines?: number; // Nombre de lignes non inspectées (pour référence)
  inspection_rate: number; // Taux = (OR Inspectés / Total OR) * 100
  delta_weekly: number;
  inspection_rate_last_wednesday: number;
  last_wednesday_date: string;
  by_atelier: { atelier: string; total: number; inspected: number; rate: number }[]; // Basé sur les OR uniques
  by_type_materiel: { type_materiel: string; total: number; inspected: number; rate: number }[]; // Basé sur les OR uniques
  by_technicien: { technicien: string; total_or: number; inspected_or: number; rate: number; equipe: string }[]; // Basé sur les OR uniques
  records: Array<{
    sn: string;
    or_segment: string;
    type_materiel: string;
    atelier: string;
    date_facture: string;
    is_inspected: string;
    technicien?: string;
    equipe?: string;
  }>;
}

export interface Quarter {
  year: number;
  quarter: number;
  label: string;
}

export async function fetchInspectionAnalytics(
  user: User | null,
  year?: number,
  quarter?: number,
  team?: string | null
): Promise<InspectionAnalyticsPayload> {
  const email = (user?.email || DEFAULT_EMAIL).trim().toLowerCase();
  const search = new URLSearchParams();
  if (year) search.set("year", String(year));
  if (quarter) search.set("quarter", String(quarter));
  if (team) search.set("team", team);

  const res = await fetch(`${BACKEND_URL}/kpi/inspection/analytics?${search.toString()}`, {
    headers: {
      "X-User-Email": email,
      ...(user?.adminPassword ? { "X-Admin-Password": user.adminPassword } : {}),
    },
  });
  if (!res.ok) {
    throw new Error("Impossible de charger les KPI d'inspection");
  }
  return res.json();
}

export async function fetchInspectionTeams(user: User | null): Promise<string[]> {
  const email = (user?.email || DEFAULT_EMAIL).trim().toLowerCase();
  const res = await fetch(`${BACKEND_URL}/kpi/inspection/teams`, {
    headers: {
      "X-User-Email": email,
      ...(user?.adminPassword ? { "X-Admin-Password": user.adminPassword } : {}),
    },
  });
  if (!res.ok) {
    throw new Error("Impossible de charger les équipes");
  }
  const data = await res.json();
  return data.teams || [];
}

export async function fetchAvailableQuarters(user: User | null): Promise<{ quarters: Quarter[] }> {
  const email = (user?.email || DEFAULT_EMAIL).trim().toLowerCase();
  const res = await fetch(`${BACKEND_URL}/kpi/inspection/quarters`, {
    headers: {
      "X-User-Email": email,
      ...(user?.adminPassword ? { "X-Admin-Password": user.adminPassword } : {}),
    },
  });
  if (!res.ok) {
    throw new Error("Impossible de charger les trimestres disponibles");
  }
  return res.json();
}

export async function fetchInspectionSnapshot(user: User | null): Promise<{
  inspection_rate: number;
  delta_weekly: number;
  total: number;
  inspected: number;
  not_inspected: number;
}> {
  const email = (user?.email || DEFAULT_EMAIL).trim().toLowerCase();
  const res = await fetch(`${BACKEND_URL}/kpi/inspection/snapshot`, {
    headers: {
      "X-User-Email": email,
      ...(user?.adminPassword ? { "X-Admin-Password": user.adminPassword } : {}),
    },
  });
  if (!res.ok) {
    throw new Error("Impossible de charger le snapshot d'inspection");
  }
  return res.json();
}

export interface InspectionHistoryItem {
  year: number;
  quarter: number;
  label: string;
  inspection_rate: number;
  total: number;
  inspected: number;
  not_inspected: number;
}

export async function fetchInspectionHistory(user: User | null): Promise<{ history: InspectionHistoryItem[] }> {
  const email = (user?.email || DEFAULT_EMAIL).trim().toLowerCase();
  const res = await fetch(`${BACKEND_URL}/kpi/inspection/history`, {
    headers: {
      "X-User-Email": email,
      ...(user?.adminPassword ? { "X-Admin-Password": user.adminPassword } : {}),
    },
  });
  if (!res.ok) {
    throw new Error("Impossible de charger l'historique d'inspection");
  }
  return res.json();
}

// ==================================================
// LLTI (Lead Time to Invoice)
// ==================================================
export async function fetchLltiSnapshot(user: User | null): Promise<{
  moyenne_llti: number;
  status: string;
  total_factures: number;
}> {
  const email = (user?.email || DEFAULT_EMAIL).trim().toLowerCase();
  const res = await fetch(`${BACKEND_URL}/kpi/llti/snapshot`, {
    headers: {
      "X-User-Email": email,
      ...(user?.adminPassword ? { "X-Admin-Password": user.adminPassword } : {}),
    },
  });
  if (!res.ok) {
    throw new Error("Impossible de charger le snapshot LLTI");
  }
  return res.json();
}

export async function fetchLltiAnalytics(user: User | null): Promise<{
  global: {
    moyenne_llti: number;
    total_factures: number;
    status: string;
  };
  by_client: Array<{
    client: string;
    moyenne_llti: number;
    total_factures: number;
  }>;
  by_or: Array<{
    or_numero: string;
    num_facture: string;
    date_facture: string;
    date_pointage: string;
    llti_jours: number;
  }>;
  distribution: {
    excellent: number;
    advanced: number;
    emerging: number;
    a_ameliorer: number;
  };
}> {
  const email = (user?.email || DEFAULT_EMAIL).trim().toLowerCase();
  const res = await fetch(`${BACKEND_URL}/kpi/llti/analytics`, {
    headers: {
      "X-User-Email": email,
      ...(user?.adminPassword ? { "X-Admin-Password": user.adminPassword } : {}),
    },
  });
  if (!res.ok) {
    throw new Error("Impossible de charger les analytics LLTI");
  }
  return res.json();
}

// Fonction utilitaire pour déterminer le badge LLTI selon les seuils
export function getLltiBadge(moyenne_llti: number): { label: string; color: string; bgColor: string } {
  if (moyenne_llti < 7) {
    return { label: "Excellent", color: "text-emerald-200", bgColor: "bg-emerald-500/20" };
  } else if (moyenne_llti < 17) {
    return { label: "Advanced", color: "text-yellow-200", bgColor: "bg-yellow-500/20" };
  } else if (moyenne_llti <= 21) {
    return { label: "Emerging", color: "text-orange-200", bgColor: "bg-orange-500/20" };
  } else {
    return { label: "À améliorer", color: "text-rose-200", bgColor: "bg-rose-500/20" };
  }
}

// Fonction utilitaire pour déterminer le badge CAT selon les seuils
export function getInspectionRateBadge(rate: number): { label: string; color: string; bgColor: string } {
  if (rate >= 65) {
    return { label: "Excellent (≥65%)", color: "text-emerald-200", bgColor: "bg-emerald-500/20" };
  } else if (rate >= 50) {
    return { label: "Alerte (50-64%)", color: "text-orange-200", bgColor: "bg-orange-500/25" };
  } else {
    return { label: "Critique (<50%)", color: "text-rose-200", bgColor: "bg-rose-500/25" };
  }
}

