import { Shield } from "lucide-react";
import { FormEvent, useState } from "react";

interface Props {
  onLogin: (email: string) => void;
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
    <div className="mx-auto max-w-md rounded-2xl border border-white/10 bg-white/5 p-8 shadow-luxe">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gold/20 text-gold">
          <Shield />
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-gold">Neemba Copilote</p>
          <h1 className="text-xl font-semibold">Connexion sécurisée</h1>
        </div>
      </div>
      <p className="mb-4 text-sm text-sand/80">
        Domaines autorisés : <span className="font-medium text-gold">@neemba.com</span>. Utilisez l'email admin pour
        débloquer l'upload.
      </p>
      <form onSubmit={submit} className="flex flex-col gap-3">
        <input
          className="field"
          type="email"
          placeholder="prenom.nom@neemba.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          className="field"
          type="password"
          placeholder="Mot de passe admin (requis si admin)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="text-sm text-rose-200">{error}</p>}
        <button type="submit" className="btn-primary">
          Continuer
        </button>
      </form>
    </div>
  );
}

export default Login;

