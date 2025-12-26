import { Layers } from "lucide-react";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import { useAuth } from "./hooks/useAuth";
import { useState } from "react";
import ProductivityDetail from "./pages/ProductivityDetail";

function App() {
  const auth = useAuth();
  const [view, setView] = useState<"dashboard" | "productivity">("dashboard");

  return (
    <div className="min-h-screen bg-gradient-to-b from-onyx to-black px-4 py-8">
      <div className="mx-auto max-w-5xl space-y-8">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gold/20 text-gold">
              <Layers />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-gold">Neemba Copilote</p>
              <h1 className="text-xl font-semibold text-sand">
                Bienvenue au Co-Pilote Méthode et Process Neemba Sénégal
              </h1>
            </div>
          </div>
          <span className="rounded-full border border-gold/30 px-3 py-1 text-xs text-gold">
            -----
          </span>
        </header>

        <section
  className="relative overflow-hidden rounded-3xl border border-[#FFD700]/20 shadow-2xl"
  style={{
    // Cette image montre un vrai tombereau de chantier (Yellow Machine)
    backgroundImage: `linear-gradient(120deg, rgba(0, 0, 0, 0.9) 0%, rgba(0, 0, 0, 0.4) 100%), url('https://images.unsplash.com/photo-1532635042-a6f6abd57685?auto=format&fit=crop&w=1600&q=80')`,
    backgroundSize: "cover",
    backgroundPosition: "center",
  }}
>
  <div className="flex flex-col gap-6 px-8 py-12 md:flex-row md:items-center md:justify-between relative z-10">
    <div className="max-w-2xl space-y-4">
      <div className="flex items-center gap-2">
        <span className="h-1 w-8 bg-[#FFD700]"></span>
        <p className="text-xs uppercase tracking-[0.3em] text-[#FFD700] font-bold">Neemba Sénégal · Productivité</p>
      </div>
      
      
      
      <p className="text-base text-gray-300 max-w-lg">
        Analyse de la productivité selon les es standards SEP 2025. 
        L'excellence opérationnelle commence par la précision des chiffres.
      </p>

      <div className="flex flex-wrap gap-3 pt-2">
        <span className="rounded-md bg-white/10 backdrop-blur-md border border-white/20 px-4 py-1.5 text-xs text-white">
          Caterpillar Excellence
        </span>
        <span className="rounded-md bg-[#FFD700]/10 backdrop-blur-md border border-[#FFD700]/30 px-4 py-1.5 text-xs text-[#FFD700]">
          Reporting @neemba.com
        </span>
      </div>
    </div>
    
    {/* La carte d'accès à droite */}
    <div className="bg-black/60 backdrop-blur-xl rounded-2xl p-6 border border-white/10 md:w-80 shadow-2xl">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-gray-400 text-xs uppercase font-medium">Flux de données</span>
          <span className="flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-yellow-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-yellow-500"></span>
          </span>
        </div>
        <p className="text-sm text-gray-200">
          En attente d'importation des fichiers <code className="text-[#FFD700]">.xlsx</code>
        </p>
        <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-yellow-600 to-[#FFD700] w-[65%]"></div>
        </div>
        <p className="text-[11px] text-gray-400 italic leading-tight">
          La productivité est calculée sur une période glissante de 12 mois (Rolling 12-months).
        </p>
      </div>
    </div>
  </div>
</section>
        {auth.user ? (
          view === "dashboard" ? (
            <Dashboard auth={auth} onOpenProductivity={() => setView("productivity")} />
          ) : (
            <ProductivityDetail auth={auth} onBack={() => setView("dashboard")} />
          )
        ) : (
          <Login onLogin={auth.login} error={auth.error} />
        )}
      </div>
    </div>
  );
}

export default App;

