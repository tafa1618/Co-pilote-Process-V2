import { useEffect, useState } from "react";
import { Card } from "@tremor/react";
import { TrendingUp, Clock, Users, Target, CheckCircle2, FileText } from "lucide-react";
import { fetchProductivity, fetchInspectionSnapshot, getInspectionRateBadge, fetchLltiSnapshot, getLltiBadge } from "../services/analytics";
import type { User } from "../types";

interface KpiSnapshotProps {
  user: User | null;
}

export function KpiSnapshot({ user }: KpiSnapshotProps) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<{
    productivite?: number;
    total_hours?: number;
    total_facturable?: number;
  } | null>(null);
  const [inspectionData, setInspectionData] = useState<{
    inspection_rate?: number;
    delta_weekly?: number;
    total?: number;
    inspected?: number;
    not_inspected?: number;
  } | null>(null);
  const [lltiData, setLltiData] = useState<{
    moyenne_llti?: number;
    status?: string;
    total_factures?: number;
  } | null>(null);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    Promise.all([
      fetchProductivity(user).catch(() => ({ global: {} })),
      fetchInspectionSnapshot(user).catch(() => null),
      fetchLltiSnapshot(user).catch(() => null),
    ])
      .then(([prodRes, inspRes, lltiRes]) => {
        setData(prodRes.global || {});
        setInspectionData(inspRes);
        setLltiData(lltiRes);
      })
      .catch(() => {
        setData(null);
        setInspectionData(null);
        setLltiData(null);
      })
      .finally(() => setLoading(false));
  }, [user]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i} className="bg-black/40 border-gold/20 animate-pulse">
            <div className="h-20" />
          </Card>
        ))}
      </div>
    );
  }

  const productivite = data?.productivite ? data.productivite * 100 : 0;
  const totalHours = data?.total_hours || 0;
  const totalFacturable = data?.total_facturable || 0;
  const inspectionRate = inspectionData?.inspection_rate || 0;
  const inspectionDelta = inspectionData?.delta_weekly || 0;
  const lltiMoyenne = lltiData?.moyenne_llti || 0;
  const lltiStatus = lltiData?.status || "N/A";
  const lltiBadge = getLltiBadge(lltiMoyenne);

  return (
    <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
      <Card className="bg-black/40 border-gold/20">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gold/10 rounded-lg text-gold">
            <TrendingUp size={20} />
          </div>
          <div>
            <p className="text-xs text-sand/60 uppercase">Productivité</p>
            <p className="text-xl font-bold text-white">{productivite.toFixed(1)}%</p>
          </div>
        </div>
      </Card>

      <Card className="bg-black/40 border-gold/20">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gold/10 rounded-lg text-gold">
            <Clock size={20} />
          </div>
          <div>
            <p className="text-xs text-sand/60 uppercase">Heures totales</p>
            <p className="text-xl font-bold text-white">{totalHours.toFixed(0)}h</p>
          </div>
        </div>
      </Card>

      <Card className="bg-black/40 border-gold/20">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gold/10 rounded-lg text-gold">
            <Target size={20} />
          </div>
          <div>
            <p className="text-xs text-sand/60 uppercase">Facturable</p>
            <p className="text-xl font-bold text-white">{totalFacturable.toFixed(0)}h</p>
          </div>
        </div>
      </Card>

      <Card className="bg-black/40 border-gold/20">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gold/10 rounded-lg text-gold">
            <Users size={20} />
          </div>
          <div>
            <p className="text-xs text-sand/60 uppercase">Cible SEP</p>
            <p className="text-xl font-bold text-white">85%</p>
          </div>
        </div>
      </Card>

      <Card className="bg-black/40 border-gold/20">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${(() => {
            const badge = getInspectionRateBadge(inspectionRate);
            return badge.bgColor.replace("bg-", "bg-").replace("/20", "/10").replace("/25", "/10");
          })()}`}>
            <CheckCircle2 size={20} className={(() => {
              const badge = getInspectionRateBadge(inspectionRate);
              return badge.color.replace("text-", "");
            })()} />
          </div>
          <div>
            <p className="text-xs text-sand/60 uppercase">Inspection Rate</p>
            <p className="text-xl font-bold text-white">{inspectionRate.toFixed(1)}%</p>
            <p className={`text-xs mt-1 ${(() => {
              const badge = getInspectionRateBadge(inspectionRate);
              return badge.color;
            })()}`}>
              {(() => {
                const badge = getInspectionRateBadge(inspectionRate);
                return badge.label;
              })()}
            </p>
            {inspectionDelta !== 0 && (
              <p className={`text-xs ${inspectionDelta >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                {inspectionDelta >= 0 ? "+" : ""}{inspectionDelta.toFixed(1)}% vs mercredi
              </p>
            )}
          </div>
        </div>
      </Card>

      <Card className="bg-black/40 border-gold/20">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${lltiBadge.bgColor}`}>
            <FileText size={20} className={lltiBadge.color} />
          </div>
          <div>
            <p className="text-xs text-sand/60 uppercase">LLTI (jours)</p>
            <p className="text-xl font-bold text-white">{lltiMoyenne.toFixed(1)}</p>
            {lltiStatus !== "N/A" && (
              <p className={`text-xs mt-1 ${lltiBadge.color}`}>
                {lltiStatus}
              </p>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}

