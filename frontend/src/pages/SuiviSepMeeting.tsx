import { useEffect, useState } from "react";
import {
  Card,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
  Select,
  SelectItem,
  TextInput,
  Button,
  Badge,
} from "@tremor/react";
import { ArrowLeft, Plus, Save, Trash2, Lock, FileText, Download, Calendar, Copy, Check } from "lucide-react";
import { KpiSnapshot } from "../components/KpiSnapshot";
import type { AuthState } from "../types";

interface LeanAction {
  id?: number;
  date_ouverture: string;
  date_cloture_prevue: string | null;
  probleme: string;
  owner: string;
  statut: "Ouvert" | "Clôturé";
  notes: string | null;
  created_at?: string;
  updated_at?: string;
}

function ActionRow({
  action,
  isEditing,
  onStartEdit,
  onCancelEdit,
  onSave,
  onDelete,
}: {
  action: LeanAction;
  isEditing: boolean;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  onSave: (updates: Partial<LeanAction>) => void;
  onDelete: () => void;
}) {
  const [editState, setEditState] = useState<Partial<LeanAction>>(action);

  useEffect(() => {
    if (isEditing) {
      setEditState(action);
    }
  }, [isEditing, action]);

  return (
    <TableRow>
      <TableCell className="text-white">{action.id}</TableCell>
      <TableCell className="text-white">
        {isEditing ? (
          <TextInput
            type="date"
            value={editState.date_ouverture || ""}
            onChange={(e) => setEditState({ ...editState, date_ouverture: e.target.value })}
            className="w-32 bg-black/60 border-gold/20 text-white text-xs"
          />
        ) : (
          action.date_ouverture
        )}
      </TableCell>
      <TableCell className="text-white">
        {isEditing ? (
          <TextInput
            type="date"
            value={editState.date_cloture_prevue || ""}
            onChange={(e) => setEditState({ ...editState, date_cloture_prevue: e.target.value || null })}
            className="w-32 bg-black/60 border-gold/20 text-white text-xs"
          />
        ) : (
          action.date_cloture_prevue || "-"
        )}
      </TableCell>
      <TableCell className="text-white">
        {isEditing ? (
          <TextInput
            value={editState.probleme || ""}
            onChange={(e) => setEditState({ ...editState, probleme: e.target.value })}
            className="w-48 bg-black/60 border-gold/20 text-white text-xs"
          />
        ) : (
          action.probleme
        )}
      </TableCell>
      <TableCell className="text-white">
        {isEditing ? (
          <TextInput
            value={editState.owner || ""}
            onChange={(e) => setEditState({ ...editState, owner: e.target.value })}
            className="w-32 bg-black/60 border-gold/20 text-white text-xs"
          />
        ) : (
          action.owner
        )}
      </TableCell>
      <TableCell>
        {isEditing ? (
          <select
            value={editState.statut || action.statut || "Ouvert"}
            onChange={(e) => {
              const newStatut = e.target.value as "Ouvert" | "Clôturé";
              setEditState((prev) => ({ ...prev, statut: newStatut }));
            }}
            className="w-28 bg-black/60 border border-gold/20 text-white text-xs px-2 py-1 rounded"
          >
            <option value="Ouvert">Ouvert</option>
            <option value="Clôturé">Clôturé</option>
          </select>
        ) : (
          <Badge color={action.statut === "Clôturé" ? "emerald" : "amber"}>
            {action.statut}
          </Badge>
        )}
      </TableCell>
      <TableCell className="text-white text-xs">
        {isEditing ? (
          <TextInput
            value={editState.notes || ""}
            onChange={(e) => setEditState({ ...editState, notes: e.target.value || null })}
            className="w-48 bg-black/60 border-gold/20 text-white text-xs"
            placeholder="Notes..."
          />
        ) : (
          action.notes || "-"
        )}
      </TableCell>
      <TableCell>
        {isEditing ? (
          <div className="flex gap-2">
            <Button
              size="xs"
              onClick={() => onSave(editState)}
              className="bg-gold text-black hover:bg-gold/80"
            >
              Sauver
            </Button>
            <Button
              size="xs"
              onClick={onCancelEdit}
              className="bg-sand/20 text-sand hover:bg-sand/30"
            >
              Annuler
            </Button>
          </div>
        ) : (
          <div className="flex gap-2">
            <Button
              size="xs"
              onClick={onStartEdit}
              className="bg-gold/20 text-gold hover:bg-gold/30"
            >
              Modifier
            </Button>
            <Button
              size="xs"
              icon={Trash2}
              onClick={onDelete}
              className="bg-red-500/20 text-red-400 hover:bg-red-500/30"
            >
              Suppr.
            </Button>
          </div>
        )}
      </TableCell>
    </TableRow>
  );
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";
const DEFAULT_EMAIL = (import.meta.env.VITE_ADMIN_EMAIL || "admin@neemba.com").trim().toLowerCase();

interface LeanAction {
  id?: number;
  date_ouverture: string;
  date_cloture_prevue: string | null;
  probleme: string;
  owner: string;
  statut: "Ouvert" | "Clôturé";
  notes: string | null;
  created_at?: string;
  updated_at?: string;
}

// ⚠️ IMPORTANT : Liste des emails autorisés pour accéder à SuiviSepMeeting
// Ajoutez les emails autorisés dans cette liste (doit correspondre au backend)
const ALLOWED_ADMINS = [
  DEFAULT_EMAIL,
  // Exemple : ajouter d'autres emails autorisés ici
  // "manager@neemba.com",
  // "directeur@neemba.com",
  // "superviseur@neemba.com",
].filter(Boolean);

export function SuiviSepMeeting({
  auth,
  onBack,
}: {
  auth: AuthState;
  onBack: () => void;
}) {
  const [actions, setActions] = useState<LeanAction[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [newAction, setNewAction] = useState<Partial<LeanAction>>({
    date_ouverture: new Date().toISOString().split("T")[0],
    statut: "Ouvert" as "Ouvert" | "Clôturé",
    probleme: "",
    owner: auth.user?.email || "",
    notes: "",
  });
  const [notesDiscussion, setNotesDiscussion] = useState<string>("");
  const [generating, setGenerating] = useState(false);
  const [archives, setArchives] = useState<any[]>([]);
  const [loadingArchives, setLoadingArchives] = useState(false);
  const [generatedMarkdown, setGeneratedMarkdown] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const userEmail = auth.user?.email?.toLowerCase() || "";
  const isAllowed = ALLOWED_ADMINS.includes(userEmail);

  useEffect(() => {
    if (!isAllowed) {
      setLoading(false);
      return;
    }
    fetchActions();
    fetchArchives();
  }, [isAllowed]);

  const fetchArchives = async () => {
    setLoadingArchives(true);
    try {
      const email = (auth.user?.email || DEFAULT_EMAIL).trim().toLowerCase();
      const res = await fetch(`${BACKEND_URL}/api/meeting-summary/list`, {
        headers: {
          "X-User-Email": email,
          ...(auth.user?.adminPassword ? { "X-Admin-Password": auth.user.adminPassword } : {}),
        },
      });
      if (!res.ok) throw new Error("Erreur lors du chargement");
      const data = await res.json();
      setArchives(data.summaries || []);
    } catch (err) {
      console.error("Erreur fetch archives:", err);
    } finally {
      setLoadingArchives(false);
    }
  };

  const handleGenerateCR = async () => {
    setGenerating(true);
    setGeneratedMarkdown(null);
    try {
      const email = (auth.user?.email || DEFAULT_EMAIL).trim().toLowerCase();
      const res = await fetch(`${BACKEND_URL}/api/meeting-summary/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-Email": email,
          ...(auth.user?.adminPassword ? { "X-Admin-Password": auth.user.adminPassword } : {}),
        },
        body: JSON.stringify({
          meeting_date: new Date().toISOString().split("T")[0],
          notes_discussion: notesDiscussion,
        }),
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Erreur lors de la génération" }));
        throw new Error(error.detail || "Erreur lors de la génération");
      }
      
      // Récupérer le Markdown
      const data = await res.json();
      setGeneratedMarkdown(data.markdown || "");
      
      // Rafraîchir les archives
      await fetchArchives();
    } catch (err: any) {
      console.error("Erreur génération CR:", err);
      alert(err.message || "Erreur lors de la génération du compte rendu");
    } finally {
      setGenerating(false);
    }
  };

  const handleCopyMarkdown = async () => {
    if (!generatedMarkdown) return;
    try {
      await navigator.clipboard.writeText(generatedMarkdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Erreur copie:", err);
      alert("Erreur lors de la copie");
    }
  };

  const handleViewCR = async (crId: number) => {
    try {
      const email = (auth.user?.email || DEFAULT_EMAIL).trim().toLowerCase();
      const res = await fetch(`${BACKEND_URL}/api/meeting-summary/${crId}`, {
        headers: {
          "X-User-Email": email,
          ...(auth.user?.adminPassword ? { "X-Admin-Password": auth.user.adminPassword } : {}),
        },
      });
      if (!res.ok) throw new Error("Erreur lors de la récupération");
      
      const data = await res.json();
      setGeneratedMarkdown(data.markdown || "");
      // Scroll vers le rapport généré
      setTimeout(() => {
        const element = document.getElementById("generated-report");
        if (element) element.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err) {
      console.error("Erreur récupération CR:", err);
      alert("Erreur lors de la récupération du compte rendu");
    }
  };

  const fetchActions = async () => {
    try {
      const email = (auth.user?.email || DEFAULT_EMAIL).trim().toLowerCase();
      const res = await fetch(`${BACKEND_URL}/api/lean-actions`, {
        headers: {
          "X-User-Email": email,
          ...(auth.user?.adminPassword ? { "X-Admin-Password": auth.user.adminPassword } : {}),
        },
      });
      if (!res.ok) throw new Error("Erreur lors du chargement");
      const data = await res.json();
      setActions(data.actions || []);
    } catch (err) {
      console.error("Erreur fetch actions:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newAction.probleme?.trim()) {
      alert("Le problème est obligatoire");
      return;
    }
    try {
      const email = (auth.user?.email || DEFAULT_EMAIL).trim().toLowerCase();
      const res = await fetch(`${BACKEND_URL}/api/lean-actions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-Email": email,
          ...(auth.user?.adminPassword ? { "X-Admin-Password": auth.user.adminPassword } : {}),
        },
        body: JSON.stringify(newAction),
      });
      if (!res.ok) throw new Error("Erreur lors de la création");
      await fetchActions();
      setNewAction({
        date_ouverture: new Date().toISOString().split("T")[0],
        statut: "Ouvert",
        probleme: "",
        owner: auth.user?.email || "",
        notes: "",
      });
    } catch (err) {
      console.error("Erreur création:", err);
      alert("Erreur lors de la création de l'action");
    }
  };

  const handleUpdate = async (id: number, updates: Partial<LeanAction>) => {
    try {
      const email = (auth.user?.email || DEFAULT_EMAIL).trim().toLowerCase();
      const res = await fetch(`${BACKEND_URL}/api/lean-actions/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-User-Email": email,
          ...(auth.user?.adminPassword ? { "X-Admin-Password": auth.user.adminPassword } : {}),
        },
        body: JSON.stringify(updates),
      });
      if (!res.ok) throw new Error("Erreur lors de la mise à jour");
      await fetchActions();
      setEditingId(null);
    } catch (err) {
      console.error("Erreur mise à jour:", err);
      alert("Erreur lors de la mise à jour");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Êtes-vous sûr de vouloir supprimer cette action ?")) return;
    try {
      const email = (auth.user?.email || DEFAULT_EMAIL).trim().toLowerCase();
      const res = await fetch(`${BACKEND_URL}/api/lean-actions/${id}`, {
        method: "DELETE",
        headers: {
          "X-User-Email": email,
          ...(auth.user?.adminPassword ? { "X-Admin-Password": auth.user.adminPassword } : {}),
        },
      });
      if (!res.ok) throw new Error("Erreur lors de la suppression");
      await fetchActions();
    } catch (err) {
      console.error("Erreur suppression:", err);
      alert("Erreur lors de la suppression");
    }
  };

  if (!isAllowed) {
    return (
      <div className="space-y-6">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gold hover:text-sand text-sm"
        >
          <ArrowLeft size={16} /> Retour
        </button>
        <Card className="bg-red-500/10 border-red-500/30">
          <div className="flex items-center gap-3">
            <Lock className="text-red-400" size={24} />
            <div>
              <h3 className="text-lg font-bold text-white">Accès Restreint</h3>
              <p className="text-sm text-sand/80">
                Vous n'avez pas les permissions nécessaires pour accéder à cette page.
              </p>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-10 text-center text-gold animate-pulse font-mono">
        Chargement des actions...
      </div>
    );
  }

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
          <h2 className="text-3xl font-bold text-white">Suivi SEP Meeting</h2>
          <p className="text-sand/60 text-sm">Actions Lean et suivi des problèmes</p>
        </div>
      </div>

      {/* KPI SNAPSHOT */}
      <KpiSnapshot user={auth.user} />

      {/* GÉNÉRATION COMPTE RENDU */}
      <Card className="bg-black/60 border-gold/20 backdrop-blur-xl">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="text-gold" size={24} />
            Génération du Compte Rendu
          </h3>
          <Button
            onClick={handleGenerateCR}
            disabled={generating}
            icon={FileText}
            className="bg-gold text-black hover:bg-gold/80 font-semibold"
          >
            {generating ? "Génération..." : "Générer le Compte Rendu"}
          </Button>
        </div>
        <div className="space-y-3">
          <div>
            <label className="text-sm text-sand/80 mb-2 block">Notes de discussion (optionnel)</label>
            <textarea
              value={notesDiscussion}
              onChange={(e) => setNotesDiscussion(e.target.value)}
              placeholder="Saisissez les notes de discussion de la réunion..."
              className="w-full bg-black/40 border-gold/20 text-white rounded-lg p-3 min-h-[100px] resize-y"
            />
          </div>
          <p className="text-xs text-sand/60">
            Le compte rendu inclura : Résumé de performance, Actions ouvertes, Actions critiques, et ces notes.
          </p>
        </div>
      </Card>

      {/* RAPPORT GÉNÉRÉ (MARKDOWN) */}
      {generatedMarkdown && (
        <Card id="generated-report" className="bg-black/60 border-gold/20 backdrop-blur-xl">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <FileText className="text-gold" size={24} />
              Rapport Généré
            </h3>
            <Button
              onClick={handleCopyMarkdown}
              icon={copied ? Check : Copy}
              className={copied ? "bg-green-600 text-white" : "bg-gold text-black hover:bg-gold/80"}
            >
              {copied ? "Copié !" : "Copier le rapport"}
            </Button>
          </div>
          <div className="bg-black/40 border border-gold/20 rounded-lg p-4">
            <pre className="text-sm text-white whitespace-pre-wrap font-mono overflow-x-auto max-h-[600px] overflow-y-auto">
              {generatedMarkdown}
            </pre>
          </div>
          <p className="text-xs text-sand/60 mt-3">
            Le rapport a été archivé. Vous pouvez le copier et l'envoyer par email ou Teams.
          </p>
        </Card>
      )}

      {/* TABLE DES ACTIONS */}
      <Card className="bg-black/60 border-gold/20 backdrop-blur-xl">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-white">Actions Lean</h3>
        </div>

        {/* Formulaire d'ajout */}
        <div className="mb-6 p-4 bg-black/40 rounded-lg border border-gold/10">
          <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
            <Plus size={18} /> Nouvelle action
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
            <TextInput
              placeholder="Problème *"
              value={newAction.probleme || ""}
              onChange={(e) => setNewAction({ ...newAction, probleme: e.target.value })}
              className="bg-black/60 border-gold/20 text-white"
            />
            <TextInput
              type="date"
              value={newAction.date_ouverture || ""}
              onChange={(e) => setNewAction({ ...newAction, date_ouverture: e.target.value })}
              className="bg-black/60 border-gold/20 text-white"
            />
            <TextInput
              type="date"
              placeholder="Date clôture prévue"
              value={newAction.date_cloture_prevue || ""}
              onChange={(e) => setNewAction({ ...newAction, date_cloture_prevue: e.target.value || null })}
              className="bg-black/60 border-gold/20 text-white"
            />
            <TextInput
              placeholder="Owner (email) *"
              value={newAction.owner || ""}
              onChange={(e) => setNewAction({ ...newAction, owner: e.target.value })}
              className="bg-black/60 border-gold/20 text-white"
            />
            <div className="flex gap-2">
              <select
                value={newAction.statut || "Ouvert"}
                onChange={(e) => {
                  const newStatut = e.target.value as "Ouvert" | "Clôturé";
                  setNewAction((prev) => ({ ...prev, statut: newStatut }));
                }}
                className="flex-1 bg-black/60 border border-gold/20 text-white px-3 py-2 rounded"
              >
                <option value="Ouvert">Ouvert</option>
                <option value="Clôturé">Clôturé</option>
              </select>
              <Button
                onClick={handleCreate}
                icon={Save}
                size="sm"
                className="bg-gold text-black hover:bg-gold/80"
              >
                Ajouter
              </Button>
            </div>
          </div>
          <TextInput
            placeholder="Notes (optionnel)"
            value={newAction.notes || ""}
            onChange={(e) => setNewAction({ ...newAction, notes: e.target.value || null })}
            className="mt-3 bg-black/60 border-gold/20 text-white"
          />
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <Table>
            <TableHead>
              <TableRow className="bg-white/5">
                <TableHeaderCell className="text-gold">ID</TableHeaderCell>
                <TableHeaderCell className="text-gold">Date ouverture</TableHeaderCell>
                <TableHeaderCell className="text-gold">Date clôture prévue</TableHeaderCell>
                <TableHeaderCell className="text-gold">Problème</TableHeaderCell>
                <TableHeaderCell className="text-gold">Owner</TableHeaderCell>
                <TableHeaderCell className="text-gold">Statut</TableHeaderCell>
                <TableHeaderCell className="text-gold">Notes</TableHeaderCell>
                <TableHeaderCell className="text-gold">Actions</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {actions.map((action) => {
                const isEditing = editingId === action.id;
                return (
                  <ActionRow
                    key={action.id}
                    action={action}
                    isEditing={isEditing}
                    onStartEdit={() => setEditingId(action.id!)}
                    onCancelEdit={() => setEditingId(null)}
                    onSave={(updates) => {
                      handleUpdate(action.id!, updates);
                      setEditingId(null);
                    }}
                    onDelete={() => handleDelete(action.id!)}
                  />
                );
              })}
            </TableBody>
          </Table>
        </div>

        {actions.length === 0 && (
          <div className="text-center py-8 text-sand/60">
            Aucune action enregistrée. Créez-en une ci-dessus.
          </div>
        )}
      </Card>

      {/* ARCHIVES DES COMPTES RENDUS */}
      <Card className="bg-black/60 border-gold/20 backdrop-blur-xl">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Calendar className="text-gold" size={24} />
            Archives des Comptes Rendus
          </h3>
        </div>

        {loadingArchives ? (
          <div className="text-center py-8 text-sand/60 animate-pulse">
            Chargement des archives...
          </div>
        ) : archives.length === 0 ? (
          <div className="text-center py-8 text-sand/60">
            Aucun compte rendu généré. Utilisez le bouton ci-dessus pour créer le premier.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHead>
                <TableRow className="bg-white/5">
                  <TableHeaderCell className="text-gold">Date réunion</TableHeaderCell>
                  <TableHeaderCell className="text-gold">Productivité</TableHeaderCell>
                  <TableHeaderCell className="text-gold">Heures</TableHeaderCell>
                  <TableHeaderCell className="text-gold">Actions ouvertes</TableHeaderCell>
                  <TableHeaderCell className="text-gold">Actions critiques</TableHeaderCell>
                  <TableHeaderCell className="text-gold">Créé par</TableHeaderCell>
                  <TableHeaderCell className="text-gold">Actions</TableHeaderCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {archives.map((archive) => (
                  <TableRow key={archive.id}>
                    <TableCell className="text-white">
                      {new Date(archive.meeting_date).toLocaleDateString("fr-FR")}
                    </TableCell>
                    <TableCell className="text-white">
                      <Badge color={archive.productivite_globale >= 85 ? "emerald" : archive.productivite_globale >= 78 ? "amber" : "red"}>
                        {archive.productivite_globale.toFixed(1)}%
                      </Badge>
                    </TableCell>
                    <TableCell className="text-white">
                      {archive.total_heures.toFixed(0)}h
                    </TableCell>
                    <TableCell className="text-white">
                      {archive.actions_ouvertes}
                    </TableCell>
                    <TableCell className="text-white">
                      {archive.actions_critiques > 0 ? (
                        <Badge color="red">{archive.actions_critiques}</Badge>
                      ) : (
                        archive.actions_critiques
                      )}
                    </TableCell>
                    <TableCell className="text-white text-xs">
                      {archive.created_by}
                    </TableCell>
                    <TableCell>
                      <Button
                        size="xs"
                        icon={FileText}
                        onClick={() => handleViewCR(archive.id)}
                        className="bg-gold/20 text-gold hover:bg-gold/30"
                      >
                        Voir
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </Card>
    </div>
  );
}

export default SuiviSepMeeting;

