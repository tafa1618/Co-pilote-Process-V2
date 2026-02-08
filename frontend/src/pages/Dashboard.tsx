import React from "react";
import { LogOut, Sparkles, Activity, TrendingUp } from "lucide-react";
import { AreaChart, Card, CategoryBar, ProgressCircle } from "@tremor/react";
import UploadArea from "../components/UploadArea";
import AgentInsightsPanel from "../components/AgentInsightsPanel";
import type { AuthState } from "../types";
import { useEffect, useMemo, useState } from "react";
import { fetchProductivity, fetchInspectionSnapshot, getInspectionRateBadge, fetchLltiSnapshot, getLltiBadge } from "../services/analytics";

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

// Les KPIs seront ajoutés au fur et à mesure

interface Props {
  auth: AuthState;
  onOpenProductivity: () => void;
  onOpenSepm?: () => void;
  onOpenInspection?: () => void;
  onOpenLlti?: () => void;
}

export function Dashboard({ auth, onOpenProductivity, onOpenSepm, onOpenInspection, onOpenLlti }: Props) {
  const { user, logout, isAdmin } = auth;
  const [granularity, setGranularity] = useState<Granularity>("Mensuel");
  const [prodValue, setProdValue] = useState<number | null>(null);
  const [prodDelta, setProdDelta] = useState<number | null>(null);
  const [prodLoading, setProdLoading] = useState(false);
  const [prodError, setProdError] = useState<string | null>(null);

  // États pour Inspection Rate
  const [inspRate, setInspRate] = useState<number | null>(null);
  const [inspDelta, setInspDelta] = useState<number | null>(null);
  const [inspLoading, setInspLoading] = useState(false);
  const [inspError, setInspError] = useState<string | null>(null);

  // États pour LLTI
  const [lltiMoyenne, setLltiMoyenne] = useState<number | null>(null);
  const [lltiStatus, setLltiStatus] = useState<string | null>(null);
  const [lltiLoading, setLltiLoading] = useState(false);
  const [lltiError, setLltiError] = useState<string | null>(null);

  const data = useMemo(() => chartData[granularity], [granularity]);

  const [mockData, setMockData] = useState<any>(null);
  const [mockLoading, setMockLoading] = useState(false);

  const MOCK_DATA_FALLBACK = {
    kpis: {
      productivity: { value: 85.0, target: 90.0, unit: "%", trend: "down", label: "Productivité Globale" },
      inspection: { value: 120, target: 100, unit: "dossiers", trend: "up", label: "Dossiers Inspectés" },
      llti: { value: 4.5, target: 3.0, unit: "jours", trend: "down", label: "LLTI Moyen" }
    },
    insights: [
      { id: 1, agent: "PerformanceWatcher", type: "warning", message: "Baisse de productivité détectée sur l'équipe A le mardi après-midi.", details: "Analyse des données sur 4 semaines montrant un pattern récurrent." },
      { id: 2, agent: "QualityGuardian", type: "success", message: "Le taux d'inspection a dépassé l'objectif de 20% cette semaine.", details: "Excellente performance suite à la mise en place du nouveau process." },
      { id: 3, agent: "ProcessOptimizer", type: "info", message: "Potentiel goulot d'étranglement identifié à l'étape de validation.", details: "Le temps moyen de validation a augmenté de 15%." }
    ],
    actions: [
      { id: 101, title: "Réorganiser les shifts du mardi", priority: "High", status: "Proposed", owner: "Manager Equipe A", description: "Décaler la pause de 15min pour éviter le creux de 15h." },
      { id: 102, title: "Formation express Inspection", priority: "Medium", status: "Proposed", owner: "Responsable Qualité", description: "Partager les bonnes pratiques de la semaine avec les autres équipes." }
    ]
  };

  useEffect(() => {
    // Mode DEMO / VALIDATION : On charge les données mockées pour tout le dashboard
    setMockLoading(true);
    setProdLoading(true);
    setInspLoading(true);
    setLltiLoading(true);

    const applyMockData = (data: any) => {
      setMockData(data);
      if (data.kpis) {
        if (data.kpis.productivity) setProdValue(data.kpis.productivity.value);
        if (data.kpis.inspection) setInspRate(data.kpis.inspection.value);
        if (data.kpis.llti) setLltiMoyenne(data.kpis.llti.value);
      }
    };

    fetch("http://localhost:8000/api/analyze/mock")
      .then((res) => res.json())
      .then((data) => applyMockData(data))
      .catch((err) => {
        console.error("Mock fetch error, using fallback", err);
        applyMockData(MOCK_DATA_FALLBACK);
      })
      .finally(() => {
        setMockLoading(false);
        setProdLoading(false);
        setInspLoading(false);
        setLltiLoading(false);
      });

    // On garde les fetchs réels en parallèle ou on les commente pour l'étape 1?
    // Pour "Validation Layout", on force le mock.

    /*
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

    // Charger les données Inspection Rate
    setInspLoading(true);
    fetchInspectionSnapshot(user)
      .then((data) => {
        setInspRate(data.inspection_rate);
        setInspDelta(data.delta_weekly);
        setInspError(null);
      })
      .catch((err) => setInspError(err.message))
      .finally(() => setInspLoading(false));

    // Charger les données LLTI
    setLltiLoading(true);
    fetchLltiSnapshot(user)
      .then((data) => {
        setLltiMoyenne(data.moyenne_llti);
        setLltiStatus(data.status);
        setLltiError(null);
      })
      .catch((err) => setLltiError(err.message))
      .finally(() => setLltiLoading(false));
    */
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
        <div className="flex gap-3 flex-wrap">
          <button
            onClick={onOpenProductivity}
            className="px-4 py-2 bg-gold text-black rounded-lg font-semibold hover:bg-gold/90 transition shadow-lg"
          >
            📊 Détail productivité
          </button>
          <button
            onClick={() => {
              if (onOpenSepm) {
                onOpenSepm();
              } else {
                alert("Accès restreint. Votre email n'est pas dans la liste des administrateurs autorisés.");
              }
            }}
            className={`px-4 py-2 rounded-lg font-semibold transition shadow-lg border-2 ${onOpenSepm
              ? "bg-gold text-black hover:bg-gold/90 border-gold/50"
              : "bg-gray-600 text-gray-300 hover:bg-gray-700 border-gray-500 cursor-not-allowed opacity-60"
              }`}
            title={onOpenSepm ? "Accéder au Suivi SEP Meeting" : "Accès restreint - Email non autorisé"}
          >
            📋 Suivi SEP Meeting
          </button>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs uppercase tracking-[0.1em] text-sand/70">Granularité</span>
          <div className="flex rounded-full border border-gold/40 bg-black/40 p-1 text-sm">
            {(["Mensuel", "Trimestriel", "YTD"] as Granularity[]).map((g) => (
              <button
                key={g}
                onClick={() => setGranularity(g)}
                className={`rounded-full px-3 py-1 transition ${granularity === g ? "bg-gold text-onyx" : "text-sand hover:text-white"
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

      <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
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

        <button
          onClick={onOpenInspection || (() => { })}
          className="group flex h-full flex-col gap-4 rounded-2xl border border-gold/30 bg-black/70 p-5 text-left shadow-luxe transition hover:-translate-y-1 hover:shadow-gold/20"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-gold">Inspection Rate</p>
              <h4 className="text-lg font-semibold text-white">Taux d'Inspection</h4>
              <p className="text-sm text-sand/60 mt-1">KPI Trimestriel</p>
            </div>
            {(() => {
              const badge = inspRate != null ? getInspectionRateBadge(inspRate) : null;
              return (
                <div className={`rounded-full px-3 py-1 text-xs ${badge ? `${badge.bgColor} ${badge.color}` : "bg-blue-500/20 text-blue-200"
                  }`}>
                  {inspRate != null ? (
                    <>
                      {inspRate.toFixed(1)}%
                      <span className="ml-1 text-[10px]">
                        {badge ? badge.label.split(" ")[0] : ""}
                      </span>
                    </>
                  ) : (
                    <Activity size={14} />
                  )}
                </div>
              );
            })()}
          </div>
          <div className="flex items-center gap-4">
            <ProgressCircle
              value={inspRate ?? 0}
              size="lg"
              color={inspRate != null ? (inspRate >= 65 ? "emerald" : inspRate >= 50 ? "orange" : "rose") : "blue"}
              tooltip="Taux d'inspection trimestriel (Cible CAT: 65%)"
            >
              <div className="text-center text-sm text-white">
                <div className="text-2xl font-semibold">
                  {inspRate != null ? `${inspRate.toFixed(1)}%` : "--"}
                </div>
                <div className="text-[11px] text-sand/70">Trimestriel</div>
              </div>
            </ProgressCircle>
            <div className="space-y-2 text-sm text-sand/80">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sand/60">Variation</span>
                <span className="font-semibold text-white">
                  {inspDelta != null
                    ? `${inspDelta >= 0 ? "+" : ""}${inspDelta.toFixed(1)}%`
                    : "--"}
                </span>
                <span className="text-sand/60">vs mercredi dernier</span>
              </div>
              <div className="text-xs text-sand/60">Ratio OR inspectés / OR facturés</div>
              {inspError && <div className="text-xs text-rose-200">Erreur: {inspError}</div>}
              {inspLoading && <div className="text-xs text-sand/60">Chargement...</div>}
            </div>
          </div>
          <div className="text-xs text-gold opacity-90 group-hover:underline">Voir le détail inspection</div>
        </button>

        <button
          onClick={onOpenLlti || (() => { })}
          className="group flex h-full flex-col gap-4 rounded-2xl border border-gold/30 bg-black/70 p-5 text-left shadow-luxe transition hover:-translate-y-1 hover:shadow-gold/20"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-gold">LLTI</p>
              <h4 className="text-lg font-semibold text-white">Lead Time to Invoice</h4>
              <p className="text-sm text-sand/60 mt-1">KPI Trimestriel</p>
            </div>
            {(() => {
              const badge = lltiMoyenne != null ? getLltiBadge(lltiMoyenne) : null;
              return (
                <div className={`rounded-full px-3 py-1 text-xs ${badge ? `${badge.bgColor} ${badge.color}` : "bg-blue-500/20 text-blue-200"
                  }`}>
                  {lltiMoyenne != null ? (
                    <>
                      {lltiMoyenne.toFixed(1)}j
                      <span className="ml-1 text-[10px]">
                        {lltiStatus || ""}
                      </span>
                    </>
                  ) : (
                    <Activity size={14} />
                  )}
                </div>
              );
            })()}
          </div>
          <div className="flex items-center gap-4">
            <ProgressCircle
              value={lltiMoyenne != null ? Math.min(lltiMoyenne * 5, 100) : 0}
              size="lg"
              color={lltiMoyenne != null ? (lltiMoyenne < 7 ? "emerald" : lltiMoyenne < 17 ? "yellow" : lltiMoyenne <= 21 ? "orange" : "rose") : "blue"}
              tooltip="LLTI moyen en jours (Cible: <7 Excellent, <17 Advanced, <=21 Emerging)"
            >
              <div className="text-center text-sm text-white">
                <div className="text-2xl font-semibold">
                  {lltiMoyenne != null ? `${lltiMoyenne.toFixed(1)}j` : "--"}
                </div>
                <div className="text-[11px] text-sand/70">Trimestriel</div>
              </div>
            </ProgressCircle>
            <div className="space-y-2 text-sm text-sand/80">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sand/60">Statut</span>
                <span className="font-semibold text-white">
                  {lltiStatus || "--"}
                </span>
              </div>
              <div className="text-xs text-sand/60">Moyenne jours entre pointage et facture</div>
              <div className="text-xs text-sand/60">Seuils: &lt;7 Excellent, &lt;17 Advanced, ≤21 Emerging</div>
              {lltiError && <div className="text-xs text-rose-200">Erreur: {lltiError}</div>}
              {lltiLoading && <div className="text-xs text-sand/60">Chargement...</div>}
            </div>
          </div>
          <div className="text-xs text-gold opacity-90 group-hover:underline">Voir le détail LLTI</div>
        </button>
      </div>

      <UploadArea user={user} isAdmin={isAdmin} />
      <AgentInsightsPanel isAdmin={isAdmin} data={mockData} loading={mockLoading} />
    </div>
  );
}

export default Dashboard;

