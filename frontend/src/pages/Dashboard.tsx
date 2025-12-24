import { LogOut, Sparkles } from "lucide-react";
import UploadArea from "../components/UploadArea";
import type { AuthState } from "../types";

interface Props {
  auth: AuthState;
}

export function Dashboard({ auth }: Props) {
  const { user, logout, isAdmin } = auth;

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

      <div className="grid gap-4 md:grid-cols-3">
        <div className="glass rounded-2xl p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-gold">Disponibilité</p>
          <h3 className="mt-2 text-xl font-semibold">Backend FastAPI</h3>
          <p className="text-sm text-sand/80">Upload in-memory, pas d'écriture disque.</p>
        </div>
        <div className="glass rounded-2xl p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-gold">Sécurité</p>
          <h3 className="mt-2 text-xl font-semibold">Emails @neemba.com</h3>
          <p className="text-sm text-sand/80">RBAC par email admin configuré.</p>
        </div>
        <div className="glass rounded-2xl p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-gold">Mode Luxe</p>
          <div className="mt-2 flex items-center gap-2">
            <Sparkles className="text-gold" />
            <span className="text-sm text-sand/90">Palette Noir & Or, mobile-first.</span>
          </div>
        </div>
      </div>

      <UploadArea user={user} isAdmin={isAdmin} />
    </div>
  );
}

export default Dashboard;

