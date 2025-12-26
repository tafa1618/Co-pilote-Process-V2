import { LogOut, Sparkles, Activity, TrendingUp } from "lucide-react";
import { AreaChart, Card, CategoryBar, ProgressCircle } from "@tremor/react";
import UploadArea from "../components/UploadArea";
import type { AuthState } from "../types";
import { useEffect, useMemo, useState } from "react";
import { fetchProductivity } from "../services/analytics";

type Granularity = "Mensuel" | "Trimestriel" | "YTD";

const chartData: Record<Granularity, Array<{ mois: string; performance: number }>> = {
  Mensuel: [
    { mois: "Jan", performance: 62 },
    { mois: "Fév", performance: 74 },
    { mois: "Mar", performance: 70 },
    { mois: "Avr", performance: 82 },
    { mois: "Mai", performance: 79 },
    { mois: "Juin", performance: 88 },
    { mois: "Juil", performance: 91 },
    { mois: "Aoû", performance: 89 },
    { mois: "Sep", performance: 93 },
    { mois: "Oct", performance: 95 },
    { mois: "Nov", performance: 97 },
    { mois: "Déc", performance: 99 },
  ],
  Trimestriel: [
    { mois: "T1", performance: 68 },
    { mois: "T2", performance: 83 },
    { mois: "T3", performance: 90 },
    { mois: "T4", performance: 98 },
  ],
  YTD: [
    { mois: "S1", performance: 72 },
    { mois: "S2", performance: 94 },
  ],
};

const kpis = Array.from({ length: 15 }, (_, i) => {
  const base = 70 + Math.round(Math.random() * 25);
  const delta = Math.round((Math.random() - 0.5) * 6 * 10) / 10;
  return {
    id: `kpi-${i + 1}`,
    label: `KPI${i + 1}`,
    value: base,
    delta,
    trend: [base - 8, base - 4, base - 2, base],
  };
});

interface Props {
  auth: AuthState;
  onOpenProductivity: () => void;
}

export function Dashboard({ auth, onOpenProductivity }: Props) {
  const { user, logout, isAdmin } = auth;
  const [granularity, setGranularity] = useState<Granularity>("Mensuel");
  const [prodValue, setProdValue] = useState<number | null>(null);
  const [prodDelta, setProdDelta] = useState<number | null>(null);
  const [prodLoading, setProdLoading] = useState(false);
  const [prodError, setProdError] = useState<string | null>(null);

  const data = useMemo(() => chartData[granularity], [granularity]);

  useEffect(() => {
    setProdLoading(true);
    fetchProductivity(user)
      .then((payload) => {
        const monthly = payload.monthly;
        if (!monthly?.length) {
          setProdValue(null);
          setProdDelta(null);
          return;
        }
        const asPct = monthly.map((m) => ({ ...m, pct: (m.productivite || 0) * 100 }));
        const current = asPct[asPct.length - 1]?.pct ?? null;
        const previous = asPct.length > 1 ? asPct[asPct.length - 2]?.pct ?? null : null;
        setProdValue(current);
        setProdDelta(previous != null && current != null ? current - previous : null);
        setProdError(null);
      })
      .catch((err) => setProdError(err.message))
      .finally(() => setProdLoading(false));
  }, [user]);

  const prodBadge = useMemo(() => {
    if (prodValue == null) return { label: "N/A", color: "border-white/20 text-sand/70" };
    if (prodValue >= 85) return { label: "Excellent (≥85%)", color: "bg-emerald-500/20 text-emerald-200" };
    if (prodValue >= 82) return { label: "Advanced (≥82%)", color: "bg-amber-500/25 text-amber-100" };
    if (prodValue >= 78) return { label: "Emerging (≥78%)", color: "bg-yellow-500/25 text-yellow-100" };
    return { label: "Sous seuil", color: "bg-rose-500/25 text-rose-100" };
  }, [prodValue]);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 rounded-2xl border border-white/10 bg-white/5 p-6 shadow-luxe">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-gold">Bienvenue</p>
          <h2 className="text-2xl font-semibold">{user?.email}</h2>
          <p className="text-sm text-sand/80">
            Rôle détecté :{" "}
            <span className="font-semibold text-gold">{isAdmin ? "Admin (upload autorisé)" : "Guest (lecture seule)"}</span>
          </p>
        </div>
        <button onClick={logout} className="btn-primary bg-white/10 text-sand hover:bg-white/20">
          <LogOut size={16} /> Déconnexion
        </button>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-gold">Dashboard</p>
          <h3 className="text-xl font-semibold text-white">Performance Caterpillar</h3>
          <p className="text-sm text-sand/80">Vue globale et KPI cliquables (données mockées).</p>
        </div>
        <button
          onClick={onOpenProductivity}
          className="btn-primary bg-gold text-onyx hover:shadow-luxe"
        >
          Détail productivité
        </button>
        <div className="flex items-center gap-2">
          <span className="text-xs uppercase tracking-[0.1em] text-sand/70">Granularité</span>
          <div className="flex rounded-full border border-gold/40 bg-black/40 p-1 text-sm">
            {(["Mensuel", "Trimestriel", "YTD"] as Granularity[]).map((g) => (
              <button
                key={g}
                onClick={() => setGranularity(g)}
                className={`rounded-full px-3 py-1 transition ${
                  granularity === g ? "bg-gold text-onyx" : "text-sand hover:text-white"
                }`}
              >
                {g}
              </button>
            ))}
          </div>
        </div>
      </div>

      <Card
        className="border border-gold/30 bg-black/60 text-sand shadow-luxe"
        style={{
          backgroundImage:
            "linear-gradient(120deg, rgba(0,0,0,0.75), rgba(0,0,0,0.35)), url('https://images.unsplash.com/photo-1508387024700-9fe5c0b38b1d?auto=format&fit=crop&w=1600&q=80')",
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-gold">Performance globale</p>
            <h4 className="text-lg font-semibold text-white">Évolution {granularity}</h4>
          </div>
          <div className="flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs text-sand/90">
            <Activity size={14} className="text-gold" />
            Données mockées
          </div>
        </div>
        <div className="mt-4">
          <AreaChart
            data={data}
            index="mois"
            categories={["performance"]}
            colors={["amber"]}
            valueFormatter={(v) => `${v} pts`}
            className="h-64"
          />
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <button
          onClick={onOpenProductivity}
          className="group flex h-full flex-col gap-4 rounded-2xl border border-gold/30 bg-black/70 p-5 text-left shadow-luxe transition hover:-translate-y-1 hover:shadow-gold/20"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-gold">Productivité</p>
              <h4 className="text-lg font-semibold text-white">Facturable / Hr_travaillée</h4>
            </div>
            <div className={`rounded-full px-3 py-1 text-xs ${prodBadge.color}`}>{prodBadge.label}</div>
          </div>
          <div className="flex items-center gap-4">
            <ProgressCircle value={prodValue ?? 0} size="lg" color="amber" tooltip="Cible SEP: 85%">
              <div className="text-center text-sm text-white">
                <div className="text-2xl font-semibold">
                  {prodValue != null ? `${(Math.round(prodValue * 10) / 10).toFixed(1)}%` : "--"}
                </div>
                <div className="text-[11px] text-sand/70">Cible 85%</div>
              </div>
            </ProgressCircle>
            <div className="space-y-2 text-sm text-sand/80">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sand/60">Variation</span>
                <span className="font-semibold text-white">
                  {prodDelta != null
                    ? `${prodDelta >= 0 ? "+" : ""}${(Math.round(prodDelta * 10) / 10).toFixed(1)} pts`
                    : "--"}
                </span>
                <span className="text-sand/60">vs mois dernier</span>
              </div>
              <div className="text-xs text-sand/60">Poids SEP: 6% · Seuils: 85% / 82% / 78%</div>
              {prodError && <div className="text-xs text-rose-200">Erreur: {prodError}</div>}
              {prodLoading && <div className="text-xs text-sand/60">Chargement...</div>}
            </div>
          </div>
          <div className="text-xs text-gold opacity-90 group-hover:underline">Voir le détail productivité</div>
        </button>

        <div className="glass rounded-2xl p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-gold">Disponibilité</p>
          <h3 className="mt-2 text-xl font-semibold">Backend FastAPI</h3>
          <p className="text-sm text-sand/80">Upload in-memory, pas d'écriture disque.</p>
        </div>
        <div className="glass rounded-2xl p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-gold">Sécurité</p>
          <h3 className="mt-2 text-xl font-semibold">Emails @neemba.com</h3>
          <p className="text-sm text-sand/80">RBAC + mot de passe admin requis.</p>
        </div>
        <div className="glass rounded-2xl p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-gold">Palette Neemba</p>
          <div className="mt-2 flex items-center gap-2">
            <Sparkles className="text-gold" />
            <span className="text-sm text-sand/90">Noir & Jaune (#FFD700), mobile-first.</span>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {kpis.map((kpi) => (
          <button
            key={kpi.id}
            className="group flex h-full flex-col gap-3 rounded-2xl border border-gold/25 bg-black/60 p-4 text-left transition hover:-translate-y-1 hover:shadow-luxe"
            onClick={() => {
              // Navigation future vers /dashboard/kpi-id
            }}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-gold">{kpi.label}</p>
                <p className="text-2xl font-semibold text-white mt-1">{kpi.value} pts</p>
              </div>
              <div className="rounded-full bg-gold/15 px-3 py-1 text-xs text-gold">
                <div className="flex items-center gap-1">
                  <TrendingUp size={14} />
                  {kpi.delta >= 0 ? `+${kpi.delta}` : kpi.delta}%
                </div>
              </div>
            </div>
            <CategoryBar
              values={kpi.trend.map((t) => Math.max(0, Math.min(100, t)))}
              markerValue={kpi.value}
              colors={["amber", "amber", "amber", "emerald"]}
            />
            <div className="text-xs text-sand/70">Cliquer pour voir le détail</div>
          </button>
        ))}
      </div>

      <UploadArea user={user} isAdmin={isAdmin} />
    </div>
  );
}

export default Dashboard;

