import { Layers } from "lucide-react";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import { useAuth } from "./hooks/useAuth";

function App() {
  const auth = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-b from-onyx to-black px-4 py-8">
      <div className="mx-auto max-w-5xl space-y-8">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gold/20 text-gold">
              <Layers />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-gold">Signare KPI</p>
              <h1 className="text-xl font-semibold text-sand">Automatisation & Contrôle</h1>
            </div>
          </div>
          <span className="rounded-full border border-gold/30 px-3 py-1 text-xs text-gold">
            Mode Luxe · FCFA Ready
          </span>
        </header>

        {auth.user ? <Dashboard auth={auth} /> : <Login onLogin={auth.login} error={auth.error} />}
      </div>
    </div>
  );
}

export default App;

