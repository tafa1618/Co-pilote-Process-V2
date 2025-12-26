import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowLeft,
  TrendingUp,
  CheckCircle2,
  Info,
} from "lucide-react";

import {
  AreaChart,
  Card,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
  Select,
  SelectItem,
  BarList,
  Badge,
} from "@tremor/react";

import { fetchProductivity, type ProductivityPayload } from "../services/analytics";
import type { AuthState } from "../types";

const statusColor = (status: string) => {
  switch (status) {
    case "Weekend OK":
      return { color: "bg-slate-200/20", text: "text-slate-200" };
    case "Travail weekend":
      return { color: "bg-purple-500/60", text: "text-white" };
    case "Non conforme":
      return { color: "bg-red-500/70", text: "text-white" };
    case "Incomplet":
      return { color: "bg-amber-400/70", text: "text-black" };
    case "Conforme":
      return { color: "bg-emerald-500/70", text: "text-white" };
    case "Surpointage":
      return { color: "bg-blue-500/70", text: "text-white" };
    default:
      return { color: "bg-white/5", text: "text-white" };
  }
};

/* ======================================================
   COMPOSANT PRINCIPAL
====================================================== */
export function ProductivityDetail({
  auth,
  onBack
}: {
  auth: AuthState;
  onBack: () => void;
}) {
  const [data, setData] = useState<ProductivityPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState<string>("");
  const [selectedTeam, setSelectedTeam] = useState<string>("");

  /* ================= FETCH ================= */
  useEffect(() => {
    setLoading(true);
    fetchProductivity(auth.user)
      .then((res) => {
        setData(res);
        if (res.exhaustivity?.periods?.length) {
          setSelectedMonth(res.exhaustivity.periods.at(-1)!);
        }
      })
      .finally(() => setLoading(false));
  }, [auth.user]);

  /* ================= EXHAUSTIVITÉ ================= */
  const availableMonths = useMemo(
    () => data?.exhaustivity?.periods ?? [],
    [data?.exhaustivity?.periods],
  );

  const exhaustivity = useMemo(() => {
    if (!data || !selectedMonth) return null;
    return data.exhaustivity?.per_period?.[selectedMonth] ?? null;
  }, [data, selectedMonth]);

  // Liste des équipes disponibles pour la période sélectionnée
  const exhaustivityTeams = useMemo(() => {
    const teams = exhaustivity ? Object.values(exhaustivity.teams || {}) : [];
    return Array.from(new Set(teams.filter(Boolean)));
  }, [exhaustivity]);

  // Sélection par défaut de l'équipe lorsqu'on change de période
  useEffect(() => {
    if (exhaustivityTeams.length && !selectedTeam) {
      setSelectedTeam(exhaustivityTeams[0]);
    }
  }, [exhaustivityTeams, selectedTeam]);

  /* ================= CORRÉLATION ================= */
  const driverTeam = data?.correlation ?? null;

  if (loading) {
    return (
      <div className="p-10 text-center text-gold animate-pulse font-mono">
        CHARGEMENT DES ANALYSES de PRoductivité…
      </div>
    );
  }

  if (!data) return null;

  /* ======================================================
     RENDER
  ====================================================== */
  return (
    <div className="space-y-10 pb-20 max-w-[1600px] mx-auto">

      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-gold hover:text-sand mb-2 text-sm"
          >
            <ArrowLeft size={16} /> Retour au dashboard
          </button>
          <h2 className="text-3xl font-bold text-white">
            Productivité & Pointages
          </h2>
        </div>

        <div className="flex items-center gap-3">
          <Badge color="amber" icon={Activity}>Source SAP / AMT</Badge>
          <div className="text-[10px] text-sand/50 uppercase text-right">
            Dernière mise à jour<br />
            {new Date().toLocaleDateString()}
          </div>
        </div>
      </div>

      {/* KPI GLOBAL */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-black/40 border-gold/20 flex items-center gap-4">
          <div className="p-3 bg-gold/10 rounded-lg text-gold">
            <TrendingUp size={24} />
          </div>
          <div>
            <p className="text-xs text-sand/60 uppercase">Productivité globale</p>
            <p className="text-2xl font-bold text-white">
              {data.global ? (data.global.productivite * 100).toFixed(1) : "--"}%
            </p>
          </div>
        </Card>

        <Card className="bg-emerald-500/5 border-emerald-500/20 md:col-span-2 flex gap-4">
          <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400">
            <Info size={24} />
          </div>
          <p className="text-sm text-emerald-100/80">
            <strong>Standard CAT :</strong> cible ≥ <b>85%</b>.  
            Les résultats actuels sont exploitables à des fins de pilotage,
            mais restent indicatifs (qualité des merges).
          </p>
        </Card>
      </div>

      {/* EXHAUSTIVITÉ */}
      <Card className="bg-black/60 border-gold/20 backdrop-blur-xl">
        <div className="flex justify-between items-center mb-6 gap-4 flex-wrap">
          <div>
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="text-emerald-400" />
              Exhaustivité des pointages
            </h3>
            <p className="text-sand/50 text-sm italic">
              Contrôle journalier – heures visibles
            </p>
          </div>

          <div className="flex gap-3 items-center flex-wrap">
            <Select
              value={selectedMonth}
              onValueChange={(v) => {
                setSelectedMonth(v);
                setSelectedTeam("");
              }}
              className="w-36"
              placeholder="Mois"
            >
              {availableMonths.map((p) => (
                <SelectItem key={p} value={p}>
                  {p}
                </SelectItem>
              ))}
            </Select>
            <Select
              value={selectedTeam}
              onValueChange={setSelectedTeam}
              className="w-40"
              placeholder="Équipe"
            >
              {exhaustivityTeams.map((team) => (
                <SelectItem key={team} value={team}>
                  {team}
                </SelectItem>
              ))}
            </Select>
          </div>
        </div>

        <div className="overflow-x-auto border border-white/5 rounded-xl">
          <Table>
            <TableHead>
              <TableRow className="bg-white/5">
                <TableHeaderCell className="sticky left-0 bg-black/80 text-gold">
                  Technicien
                </TableHeaderCell>
                {Array.from({ length: 31 }, (_, i) => (
                  <TableHeaderCell key={i} className="text-[10px] text-center">
                    {i + 1}
                  </TableHeaderCell>
                ))}
              </TableRow>
            </TableHead>

            <TableBody>
              {Object.entries(exhaustivity?.statuts || {})
                .filter(([tech]) => {
                  if (!selectedTeam) return true;
                  return exhaustivity?.teams?.[tech] === selectedTeam;
                })
                .map(([tech, days]) => {
                const hoursRow = exhaustivity?.heures?.[tech] || {};
                return (
                  <TableRow key={tech}>
                    <TableCell className="sticky left-0 bg-black/80 text-white text-xs">
                      {tech}
                    </TableCell>
                    {Array.from({ length: 31 }, (_, i) => {
                      const day = (i + 1).toString();
                      const status = days[day] as string | undefined;
                      const hours = hoursRow[day] ?? 0;
                      const cfg = statusColor(status || "");
                      return (
                        <TableCell key={i} className="p-0.5">
                          <div
                            title={`${tech} – Jour ${day} : ${hours}h${status ? ` (${status})` : ""}`}
                            className={`h-8 rounded-sm flex items-center justify-center ${cfg.color} ${cfg.text} text-[10px] font-bold`}
                          >
                            {hours > 0 ? hours.toFixed(1) : ""}
                          </div>
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </Card>

      {/* ÉVOLUTION + ANALYSE */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <Card className="lg:col-span-2 bg-black/40 border-gold/20">
          <h4 className="text-white font-bold mb-2">Évolution mensuelle</h4>
          <AreaChart
            className="h-80"
            data={data.monthly}
            index="mois"
            categories={["productivite"]}
            colors={["amber"]}
            valueFormatter={(v) => `${(v * 100).toFixed(1)}%`}
          />
        </Card>

        <div className="space-y-6">
          {driverTeam && (
            <Card className="bg-gold/5 border-gold/40">
              <h4 className="text-gold font-bold uppercase text-xs mb-2">
                Équipe driver
              </h4>
              <p className="text-white">
                <b>{driverTeam.equipe}</b> pilote la performance globale.
              </p>
              <p className="text-sm text-sand/60 mt-2">
                Corrélation : {(driverTeam.score * 100).toFixed(0)}%
              </p>
            </Card>
          )}

          <Card className="bg-black/40 border-gold/20">
            <h4 className="text-white font-semibold text-sm mb-4">
              Top techniciens (productivité)
            </h4>
            <BarList
              data={data.technicians.slice(0, 5).map((t) => ({
                name: t["Salarié - Nom"] || "N/A",
                value: (t.productivite || 0) * 100,
              }))}
              valueFormatter={(v: number) => `${v.toFixed(1)}%`}
              color="amber"
            />
          </Card>
        </div>
      </div>
    </div>
  );
}

export default ProductivityDetail;

