import { useState, useEffect } from "react";
import { ArrowLeft, Calendar } from "lucide-react";
import { Select, SelectItem } from "@tremor/react";
import { fetchAvailableQuarters, fetchInspectionTeams, type Quarter } from "../services/analytics";
import type { AuthState } from "../types";

const STREAMLIT_URL = import.meta.env.VITE_STREAMLIT_URL || "http://localhost:8501";

function InspectionDetail({
  auth,
  onBack,
}: {
  auth: AuthState;
  onBack: () => void;
}) {
  const [availableQuarters, setAvailableQuarters] = useState<Quarter[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [selectedQuarter, setSelectedQuarter] = useState<number | null>(null);
  const [availableTeams, setAvailableTeams] = useState<string[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);

  useEffect(() => {
    fetchAvailableQuarters(auth.user)
      .then((res) => {
        setAvailableQuarters(res.quarters);
        if (res.quarters.length > 0) {
          const current = res.quarters[0];
          setSelectedYear(current.year);
          setSelectedQuarter(current.quarter);
        }
      })
      .catch((err) => {
        console.error("Erreur chargement trimestres:", err);
      });

    fetchInspectionTeams(auth.user)
      .then((teams) => {
        setAvailableTeams(teams);
      })
      .catch((err) => {
        console.error("Erreur chargement équipes:", err);
      });
  }, [auth.user]);

  // Construire l'URL de l'iframe avec les paramètres
  const iframeUrl = (() => {
    const params = new URLSearchParams();
    params.set("kpi", "inspection");
    if (selectedYear) params.set("year", String(selectedYear));
    if (selectedQuarter) params.set("quarter", String(selectedQuarter));
    if (selectedTeam) params.set("team", selectedTeam);
    return `${STREAMLIT_URL}?${params.toString()}`;
  })();

  const currentQuarter = availableQuarters.find(
    (q) => q.year === selectedYear && q.quarter === selectedQuarter
  );

  return (
    <div className="space-y-6 pb-20 max-w-[1600px] mx-auto">
      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-gold hover:text-sand mb-2 text-sm"
          >
            <ArrowLeft size={16} /> Retour au dashboard
          </button>
          <h2 className="text-3xl font-bold text-white">Inspection Rate</h2>
          <p className="text-sand/60 text-sm">KPI Trimestriel - Taux d'inspection des matériels</p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <Calendar className="text-gold" size={20} />
          <Select
            value={currentQuarter?.label || ""}
            onValueChange={(v: string) => {
              const q = availableQuarters.find((q) => q.label === v);
              if (q) {
                setSelectedYear(q.year);
                setSelectedQuarter(q.quarter);
              }
            }}
            className="w-48 bg-black/60 border-gold/20"
          >
            {availableQuarters.map((q) => (
              <SelectItem key={q.label} value={q.label}>
                {q.label}
              </SelectItem>
            ))}
          </Select>
          <Select
            value={selectedTeam || "all"}
            onValueChange={(v: string) => {
              setSelectedTeam(v === "all" ? null : v);
            }}
            className="w-48 bg-black/60 border-gold/20"
          >
            <SelectItem value="all">Toutes les équipes</SelectItem>
            {availableTeams.map((team) => (
              <SelectItem key={team} value={team}>
                {team}
              </SelectItem>
            ))}
          </Select>
        </div>
      </div>

      {/* IFRAME STREAMLIT */}
      <div className="w-full h-[calc(100vh-200px)] border border-gold/30 rounded-lg overflow-hidden bg-black/40">
        <iframe
          src={iframeUrl}
          className="w-full h-full border-0"
          title="Inspection Rate Detail"
          allow="fullscreen"
        />
      </div>
    </div>
  );
}

export default InspectionDetail;
