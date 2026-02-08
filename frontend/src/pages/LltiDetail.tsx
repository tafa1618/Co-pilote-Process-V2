import { useState, useEffect } from "react";
import { ArrowLeft } from "lucide-react";
import { fetchLltiAnalytics } from "../services/analytics";
import type { AuthState } from "../types";

const STREAMLIT_URL = import.meta.env.VITE_STREAMLIT_URL || "http://localhost:8501";

function LltiDetail({
  auth,
  onBack,
}: {
  auth: AuthState;
  onBack: () => void;
}) {
  // Construire l'URL de l'iframe (LLTI est trimestriel, pas besoin de filtres complexes)
  const iframeUrl = `${STREAMLIT_URL}?kpi=llti`;

  return (
    <div className="space-y-6 pb-20 max-w-[1600px] mx-auto">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-gold hover:text-sand mb-2 text-sm"
          >
            <ArrowLeft size={16} /> Retour
          </button>
          <h2 className="text-3xl font-bold text-white">💰 LLTI – Lead Time Facturation Service</h2>
          <p className="text-sand/60 text-sm">
            ⚠️ Indicateur à titre indicatif – basé sur la facturation BO et le dernier pointage connu. 
            Certaines données peuvent être perdues lors des consolidations.
          </p>
        </div>
      </div>

      {/* IFRAME STREAMLIT */}
      <div className="w-full h-[calc(100vh-200px)] border border-gold/30 rounded-lg overflow-hidden bg-black/40">
        <iframe
          src={iframeUrl}
          className="w-full h-full border-0"
          title="LLTI Detail"
          allow="fullscreen"
        />
      </div>
    </div>
  );
}

export default LltiDetail;

