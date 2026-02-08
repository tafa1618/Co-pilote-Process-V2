import { Shield } from "lucide-react";
import { FormEvent, useState } from "react";

interface Props {
  onLogin: (email: string, adminPassword?: string) => void;
  error?: string | null;
}

export function Login({ onLogin, error }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submit = (event: FormEvent) => {
    event.preventDefault();
    onLogin(email, password || undefined);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-md w-full rounded-2xl border-2 border-cat-yellow/30 bg-black/60 backdrop-blur-sm p-8 shadow-2xl">
        {/* Header with NEEMBA CAT Branding */}
        <div className="mb-6 text-center">
          <div className="flex justify-center mb-4">
            <div className="h-16 w-16 bg-cat-yellow rounded-xl flex items-center justify-center shadow-lg">
              <Shield className="text-onyx" size={32} />
            </div>
          </div>
          <h1 className="text-3xl font-black text-white mb-1">
            NEEMBA <span className="text-cat-yellow">CAT</span>
          </h1>
          <p className="text-xs text-cat-yellow/70 uppercase tracking-wider font-semibold">
            Digital Twin • Service Excellence Program
          </p>
        </div>

        <div className="mb-6 p-4 rounded-lg bg-cat-yellow/10 border border-cat-yellow/30">
          <p className="text-sm text-sand">
            <span className="font-bold text-cat-yellow">Accès réservé :</span> Seuls les emails{" "}
            <span className="font-mono text-cat-yellow">@neemba.com</span> sont autorisés.
          </p>
          <p className="text-xs text-sand/70 mt-2">
            📧 <span className="font-mono">admin-sep@neemba.com</span> dispose des droits administrateur complets.
          </p>
        </div>

        <form onSubmit={submit} className="flex flex-col gap-4">
          <input
            className="rounded-lg bg-onyx/60 border-2 border-white/20 px-4 py-3 text-sand placeholder:text-sand/50 focus:border-cat-yellow focus:outline-none"
            type="email"
            placeholder="prenom.nom@neemba.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            className="rounded-lg bg-onyx/60 border-2 border-white/20 px-4 py-3 text-sand placeholder:text-sand/50 focus:border-cat-yellow focus:outline-none"
            type="password"
            placeholder="Mot de passe (optionnel si non-admin)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && (
            <p className="text-sm text-red-300 bg-red-500/20 border border-red-500/30 rounded px-3 py-2">
              {error}
            </p>
          )}
          <button
            type="submit"
            className="px-6 py-3 rounded-lg bg-cat-yellow text-onyx font-bold hover:bg-cat-yellow/90 transition-all shadow-lg"
          >
            Se connecter →
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
