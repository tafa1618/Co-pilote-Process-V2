import { Layers, LogOut } from "lucide-react";
import Dashboard from "./pages/Dashboard";
import { Login } from "./pages/Login";
import SEPDashboard from "./pages/SEPDashboard";
import TestDashboard from "./pages/TestDashboard";
import { useAuth } from "./hooks/useAuth";
import { useState, useMemo } from "react";
import ProductivityDetail from "./pages/ProductivityDetail";
import SuiviSepMeeting from "./pages/SuiviSepMeeting";
import InspectionDetail from "./pages/InspectionDetail";
import LltiDetail from "./pages/LltiDetail";

// ⚠️ IMPORTANT : Liste des emails autorisés pour accéder à SuiviSepMeeting et Admin
// Seul admin-sep@neemba.com dispose des droits administrateur complets
const ALLOWED_ADMINS = [
  "admin-sep@neemba.com",  // Admin SEP avec droits complets (gestion fichiers + agents)
  // Ajoutez d'autres administrateurs ici si nécessaire
].map(email => email.trim().toLowerCase());

function App() {
  const auth = useAuth();
  const [view, setView] = useState<"dashboard" | "test" | "sep" | "productivity" | "sepm" | "inspection" | "llti">("sep");

  console.log("🔍 App rendering - auth.user:", auth.user);

  const canAccessSepm = useMemo(() => {
    if (!auth.user?.email) return false;
    const userEmail = auth.user.email.toLowerCase();
    const isAllowed = ALLOWED_ADMINS.includes(userEmail);
    console.log("🔍 Debug Suivi SEP Meeting:", {
      userEmail,
      allowedAdmins: ALLOWED_ADMINS,
      isAllowed,
    });
    return isAllowed;
  }, [auth.user?.email]);

  return (
    <div className="min-h-screen bg-onyx">
      <div className="space-y-0">
        {/* Modern NEEMBA CAT Header */}
        <header className="bg-gradient-to-r from-onyx to-black border-b-2 border-cat-yellow/30">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              {/* Logo and Title */}
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 bg-cat-yellow rounded-xl flex items-center justify-center shadow-lg">
                  <Layers className="text-onyx" size={28} />
                </div>
                <div>
                  <h1 className="text-2xl font-black text-white">
                    NEEMBA <span className="text-cat-yellow">CAT</span>
                  </h1>
                  <p className="text-xs text-cat-yellow/70 uppercase tracking-wider font-semibold">
                    Digital Twin • Service Excellence Program
                  </p>
                </div>
              </div>

              {/* User Actions */}
              <div className="flex items-center gap-3">
                {auth.user && (
                  <>
                    <button
                      onClick={() => setView("sep")}
                      className="px-4 py-2 rounded-lg bg-cat-yellow/10 hover:bg-cat-yellow/20 text-cat-yellow font-semibold transition-all border border-cat-yellow/30"
                    >
                      📊 Dashboard SEP
                    </button>

                    {/* Admin button - only visible for admin users */}
                    {canAccessSepm && (
                      <button
                        onClick={() => setView("sepm")}
                        className="px-4 py-2 rounded-lg font-semibold transition-all border bg-cat-yellow text-onyx hover:bg-cat-yellow/90 border-cat-yellow"
                        title="Suivi SEP Meeting"
                      >
                        📋 Admin
                      </button>
                    )}

                    <button
                      onClick={auth.logout}
                      className="px-3 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-300 font-semibold transition-all border border-red-500/30 flex items-center gap-2"
                      title="Déconnexion"
                    >
                      <LogOut size={18} />
                    </button>
                  </>
                )}
                {auth.user && (
                  <div className="h-8 w-8 rounded-full bg-cat-yellow/20 flex items-center justify-center text-cat-yellow text-xs font-bold">
                    {auth.user?.email?.[0]?.toUpperCase() || "?"}
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Main Content - Routing based on authentication */}
        {auth.user ? (
          view === "sep" ? (
            <SEPDashboard user={auth.user} isAdmin={canAccessSepm} />
          ) : view === "dashboard" ? (
            <Dashboard
              auth={auth}
              onOpenProductivity={() => setView("productivity")}
              onOpenSepm={canAccessSepm ? () => setView("sepm") : undefined}
              onOpenInspection={() => setView("inspection")}
              onOpenLlti={() => setView("llti")}
            />
          ) : view === "productivity" ? (
            <ProductivityDetail auth={auth} onBack={() => setView("sep")} />
          ) : view === "sepm" ? (
            <SuiviSepMeeting auth={auth} onBack={() => setView("sep")} />
          ) : view === "inspection" ? (
            <InspectionDetail auth={auth} onBack={() => setView("sep")} />
          ) : view === "llti" ? (
            <LltiDetail auth={auth} onBack={() => setView("sep")} />
          ) : null
        ) : (
          <Login onLogin={auth.login} error={auth.error} />
        )}
      </div>
    </div>
  );
}

export default App;
