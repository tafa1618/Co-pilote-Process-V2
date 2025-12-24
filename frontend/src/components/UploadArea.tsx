import { UploadCloud, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { useUpload } from "../hooks/useUpload";
import type { User } from "../types";

interface Props {
  user: User | null;
  isAdmin: boolean;
}

export function UploadArea({ user, isAdmin }: Props) {
  const [hovered, setHovered] = useState(false);
  const { upload, loading, error, result } = useUpload(user);

  if (!isAdmin) {
    return null;
  }

  const handleFile = (fileList: FileList | null) => {
    if (fileList && fileList[0]) {
      upload(fileList[0]);
    }
  };

  return (
    <div className="glass rounded-2xl p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-gold">Upload KPI</p>
          <h3 className="text-lg font-semibold">Glissez-déposez votre CSV / Excel</h3>
        </div>
        <ShieldCheck className="text-gold" />
      </div>

      <div
        className={`mt-4 flex min-h-[180px] cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-gold/40 bg-white/5 transition ${
          hovered ? "border-gold bg-gold/5" : ""
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setHovered(true);
        }}
        onDragLeave={() => setHovered(false)}
        onDrop={(e) => {
          e.preventDefault();
          setHovered(false);
          handleFile(e.dataTransfer.files);
        }}
        onClick={() => document.getElementById("kpi-file")?.click()}
      >
        <UploadCloud className="mb-3 h-10 w-10 text-gold" />
        <p className="text-sm text-sand/80">Déposez un fichier ou cliquez pour sélectionner</p>
        <input
          id="kpi-file"
          type="file"
          accept=".csv,.xlsx,.xls"
          className="hidden"
          onChange={(e) => handleFile(e.target.files)}
        />
      </div>

      <div className="mt-4 flex flex-col gap-2 text-sm text-sand/90">
        <p>
          Rôle détecté :{" "}
          <span className="font-semibold text-gold">{user?.role === "admin" ? "Admin" : "Guest"}</span>
        </p>
        {loading && <p>Lecture et simulation d'insertion...</p>}
        {error && <p className="text-rose-200">Erreur : {error}</p>}
        {result && (
          <div className="rounded-lg border border-gold/30 bg-white/5 p-3">
            <p className="font-semibold text-gold">{result.message}</p>
            <p className="mt-1">Lignes détectées : {result.kpi.rows}</p>
            <p className="mt-1">Colonnes (aperçu) : {result.kpi.columns.join(", ")}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default UploadArea;

