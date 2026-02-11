import { useState, useEffect } from "react";
import {
    ArrowLeft,
    Plus,
    Trash2,
    Save,
    FileText,
    Send,
    Copy,
    Check,
    UserPlus,
    Users,
} from "lucide-react";
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
}

interface Participant {
    id: string;
    name: string;
    email: string;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

export function MeetingSEP({ auth, onBack }: { auth: AuthState; onBack: () => void }) {
    const [actions, setActions] = useState<LeanAction[]>([]);
    const [participants, setParticipants] = useState<Participant[]>([]);
    const [newParticipant, setNewParticipant] = useState({ name: "", email: "" });
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [newAction, setNewAction] = useState<Partial<LeanAction>>({
        date_ouverture: new Date().toISOString().split("T")[0],
        statut: "Ouvert",
        probleme: "",
        owner: auth.user?.email || "",
        notes: "",
    });
    const [notesDiscussion, setNotesDiscussion] = useState("");
    const [generating, setGenerating] = useState(false);
    const [generatedMarkdown, setGeneratedMarkdown] = useState<string | null>(null);
    const [copied, setCopied] = useState(false);
    const [showEmailModal, setShowEmailModal] = useState(false);
    const [sending, setSending] = useState(false);

    useEffect(() => {
        fetchActions();
    }, []);

    const fetchActions = async () => {
        try {
            const email = (auth.user?.email || "").trim().toLowerCase();
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

    const handleCreateAction = async () => {
        if (!newAction.probleme?.trim()) {
            alert("Le problème est obligatoire");
            return;
        }
        try {
            const email = (auth.user?.email || "").trim().toLowerCase();
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

    const handleUpdateAction = async (id: number, updates: Partial<LeanAction>) => {
        try {
            const email = (auth.user?.email || "").trim().toLowerCase();
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

    const handleDeleteAction = async (id: number) => {
        if (!confirm("Êtes-vous sûr de vouloir supprimer cette action ?")) return;
        try {
            const email = (auth.user?.email || "").trim().toLowerCase();
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

    const handleGenerateCR = async () => {
        setGenerating(true);
        setGeneratedMarkdown(null);
        try {
            const email = (auth.user?.email || "").trim().toLowerCase();
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

            const data = await res.json();
            setGeneratedMarkdown(data.markdown || "");
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

    const handleAddParticipant = () => {
        if (!newParticipant.name.trim() || !newParticipant.email.trim()) {
            alert("Nom et email sont obligatoires");
            return;
        }
        const participant: Participant = {
            id: Math.random().toString(36).substr(2, 9),
            name: newParticipant.name,
            email: newParticipant.email,
        };
        setParticipants([...participants, participant]);
        setNewParticipant({ name: "", email: "" });
    };

    const handleRemoveParticipant = (id: string) => {
        setParticipants(participants.filter((p) => p.id !== id));
    };

    const handleSendEmail = async () => {
        if (participants.length === 0) {
            alert("Ajoutez au moins un participant");
            return;
        }
        if (!generatedMarkdown) {
            alert("Générez d'abord le compte rendu");
            return;
        }

        setSending(true);
        try {
            const email = (auth.user?.email || "").trim().toLowerCase();
            const recipients = participants.map((p) => p.email);
            const subject = `CR Meeting SEP - ${new Date().toLocaleDateString("fr-FR")}`;

            const res = await fetch(`${BACKEND_URL}/api/admin/send-meeting-cr`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-User-Email": email,
                    ...(auth.user?.adminPassword ? { "X-Admin-Password": auth.user.adminPassword } : {}),
                },
                body: JSON.stringify({
                    recipients,
                    subject,
                    markdown: generatedMarkdown,
                }),
            });

            if (!res.ok) throw new Error("Erreur lors de l'envoi");

            alert(`CR envoyé avec succès à ${participants.length} participant(s) !`);
            setShowEmailModal(false);
        } catch (err) {
            console.error("Erreur envoi email:", err);
            alert("Erreur lors de l'envoi du CR. Vérifiez la configuration email du backend.");
        } finally {
            setSending(false);
        }
    };

    if (loading) {
        return (
            <div className="p-10 text-center text-cat-yellow animate-pulse font-mono">
                Chargement...
            </div>
        );
    }

    return (
        <div className="space-y-6 pb-20 max-w-[1600px] mx-auto px-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <button
                        onClick={onBack}
                        className="flex items-center gap-2 text-cat-yellow hover:text-cat-yellow/80 mb-2 text-sm transition-colors"
                    >
                        <ArrowLeft size={16} /> Retour
                    </button>
                    <h2 className="text-3xl font-bold text-white">📅 Meeting SEP</h2>
                    <p className="text-sand/60 text-sm">
                        Réunion du {new Date().toLocaleDateString("fr-FR", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
                    </p>
                </div>
            </div>

            {/* KPI Snapshot */}
            <KpiSnapshot user={auth.user} />

            {/* KPI Weekly Comparison */}
            <div className="bg-black/60 border-2 border-cat-yellow/30 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-center gap-3 mb-6">
                    <div className="h-10 w-10 bg-cat-yellow/20 rounded-lg flex items-center justify-center">
                        <FileText className="text-cat-yellow" size={20} />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">Évolution Hebdomadaire des KPIs</h3>
                        <p className="text-xs text-sand/60">
                            Comparaison semaine actuelle vs semaine précédente
                        </p>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-white/10">
                                <th className="text-left text-cat-yellow text-sm font-semibold p-3">KPI</th>
                                <th className="text-center text-cat-yellow text-sm font-semibold p-3">Semaine N-1</th>
                                <th className="text-center text-cat-yellow text-sm font-semibold p-3">Semaine N</th>
                                <th className="text-center text-cat-yellow text-sm font-semibold p-3">Variation</th>
                                <th className="text-center text-cat-yellow text-sm font-semibold p-3">Tendance</th>
                            </tr>
                        </thead>
                        <tbody>
                            {/* Tech Productivity */}
                            <tr className="border-b border-white/5 hover:bg-white/5">
                                <td className="text-white font-medium p-3">Tech Productivity</td>
                                <td className="text-center text-white p-3">80.2%</td>
                                <td className="text-center text-white p-3">82.5%</td>
                                <td className="text-center p-3">
                                    <span className="px-2 py-1 rounded bg-green-500/20 text-green-300 text-sm font-semibold">
                                        +2.3%
                                    </span>
                                </td>
                                <td className="text-center p-3">
                                    <span className="text-green-400 text-xl">↑</span>
                                </td>
                            </tr>

                            {/* Tech Capacity */}
                            <tr className="border-b border-white/5 hover:bg-white/5">
                                <td className="text-white font-medium p-3">Tech Capacity</td>
                                <td className="text-center text-white p-3">1200h</td>
                                <td className="text-center text-white p-3">1250h</td>
                                <td className="text-center p-3">
                                    <span className="px-2 py-1 rounded bg-green-500/20 text-green-300 text-sm font-semibold">
                                        +4.2%
                                    </span>
                                </td>
                                <td className="text-center p-3">
                                    <span className="text-green-400 text-xl">↑</span>
                                </td>
                            </tr>

                            {/* Inspection Rate */}
                            <tr className="border-b border-white/5 hover:bg-white/5">
                                <td className="text-white font-medium p-3">Inspection Rate</td>
                                <td className="text-center text-white p-3">68.5%</td>
                                <td className="text-center text-white p-3">65.2%</td>
                                <td className="text-center p-3">
                                    <span className="px-2 py-1 rounded bg-red-500/20 text-red-300 text-sm font-semibold">
                                        -3.3%
                                    </span>
                                </td>
                                <td className="text-center p-3">
                                    <span className="text-red-400 text-xl">↓</span>
                                </td>
                            </tr>

                            {/* LLTI */}
                            <tr className="border-b border-white/5 hover:bg-white/5">
                                <td className="text-white font-medium p-3">LLTI</td>
                                <td className="text-center text-white p-3">9.2j</td>
                                <td className="text-center text-white p-3">8.5j</td>
                                <td className="text-center p-3">
                                    <span className="px-2 py-1 rounded bg-green-500/20 text-green-300 text-sm font-semibold">
                                        -7.6%
                                    </span>
                                </td>
                                <td className="text-center p-3">
                                    <span className="text-green-400 text-xl">↓</span>
                                </td>
                            </tr>

                            {/* Data Quality */}
                            <tr className="border-b border-white/5 hover:bg-white/5">
                                <td className="text-white font-medium p-3">Data Quality</td>
                                <td className="text-center text-white p-3">93.1%</td>
                                <td className="text-center text-white p-3">94.8%</td>
                                <td className="text-center p-3">
                                    <span className="px-2 py-1 rounded bg-green-500/20 text-green-300 text-sm font-semibold">
                                        +1.7%
                                    </span>
                                </td>
                                <td className="text-center p-3">
                                    <span className="text-green-400 text-xl">↑</span>
                                </td>
                            </tr>

                            {/* Service Response */}
                            <tr className="border-b border-white/5 hover:bg-white/5">
                                <td className="text-white font-medium p-3">Service Response</td>
                                <td className="text-center text-white p-3">1.5h</td>
                                <td className="text-center text-white p-3">1.2h</td>
                                <td className="text-center p-3">
                                    <span className="px-2 py-1 rounded bg-green-500/20 text-green-300 text-sm font-semibold">
                                        -20.0%
                                    </span>
                                </td>
                                <td className="text-center p-3">
                                    <span className="text-green-400 text-xl">↓</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                {/* Summary */}
                <div className="mt-4 p-4 bg-onyx/60 border border-cat-yellow/10 rounded-lg">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                        <div>
                            <p className="text-sand/60 text-xs mb-1">KPIs en amélioration</p>
                            <p className="text-2xl font-bold text-green-400">5</p>
                        </div>
                        <div>
                            <p className="text-sand/60 text-xs mb-1">KPIs en dégradation</p>
                            <p className="text-2xl font-bold text-red-400">1</p>
                        </div>
                        <div>
                            <p className="text-sand/60 text-xs mb-1">KPIs stables</p>
                            <p className="text-2xl font-bold text-gray-400">0</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Participants Section */}
            <div className="bg-black/60 border-2 border-cat-yellow/30 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-center gap-3 mb-4">
                    <div className="h-10 w-10 bg-cat-yellow/20 rounded-lg flex items-center justify-center">
                        <Users className="text-cat-yellow" size={20} />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">Participants</h3>
                        <p className="text-xs text-sand/60">
                            Ajoutez les participants pour l'envoi automatique du CR
                        </p>
                    </div>
                </div>

                {/* Add Participant Form */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                    <input
                        type="text"
                        placeholder="Nom du participant"
                        value={newParticipant.name}
                        onChange={(e) => setNewParticipant({ ...newParticipant, name: e.target.value })}
                        className="bg-onyx/60 border border-white/20 rounded-lg px-4 py-2 text-white placeholder:text-sand/50 focus:border-cat-yellow focus:outline-none"
                    />
                    <input
                        type="email"
                        placeholder="Email"
                        value={newParticipant.email}
                        onChange={(e) => setNewParticipant({ ...newParticipant, email: e.target.value })}
                        className="bg-onyx/60 border border-white/20 rounded-lg px-4 py-2 text-white placeholder:text-sand/50 focus:border-cat-yellow focus:outline-none"
                    />
                    <button
                        onClick={handleAddParticipant}
                        className="px-4 py-2 bg-cat-yellow text-onyx font-semibold rounded-lg hover:bg-cat-yellow/90 transition-all flex items-center justify-center gap-2"
                    >
                        <UserPlus size={18} />
                        Ajouter
                    </button>
                </div>

                {/* Participants List */}
                {participants.length > 0 && (
                    <div className="space-y-2">
                        {participants.map((participant) => (
                            <div
                                key={participant.id}
                                className="flex items-center justify-between bg-onyx/60 border border-white/10 rounded-lg p-3"
                            >
                                <div>
                                    <p className="text-white font-medium">{participant.name}</p>
                                    <p className="text-sand/60 text-sm">{participant.email}</p>
                                </div>
                                <button
                                    onClick={() => handleRemoveParticipant(participant.id)}
                                    className="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-300 transition-all"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Lean Actions Section */}
            <div className="bg-black/60 border-2 border-cat-yellow/30 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-center gap-3 mb-6">
                    <h3 className="text-xl font-bold text-white">📝 Actions Lean</h3>
                </div>

                {/* New Action Form */}
                <div className="mb-6 p-4 bg-onyx/60 rounded-lg border border-cat-yellow/10">
                    <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                        <Plus size={18} /> Nouvelle action
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                        <input
                            type="text"
                            placeholder="Problème *"
                            value={newAction.probleme || ""}
                            onChange={(e) => setNewAction({ ...newAction, probleme: e.target.value })}
                            className="bg-black/60 border border-white/20 rounded-lg px-3 py-2 text-white placeholder:text-sand/50 focus:border-cat-yellow focus:outline-none"
                        />
                        <input
                            type="text"
                            placeholder="Owner (email) *"
                            value={newAction.owner || ""}
                            onChange={(e) => setNewAction({ ...newAction, owner: e.target.value })}
                            className="bg-black/60 border border-white/20 rounded-lg px-3 py-2 text-white placeholder:text-sand/50 focus:border-cat-yellow focus:outline-none"
                        />
                        <input
                            type="date"
                            placeholder="Deadline"
                            value={newAction.date_cloture_prevue || ""}
                            onChange={(e) => setNewAction({ ...newAction, date_cloture_prevue: e.target.value || null })}
                            className="bg-black/60 border border-white/20 rounded-lg px-3 py-2 text-white focus:border-cat-yellow focus:outline-none"
                        />
                        <button
                            onClick={handleCreateAction}
                            className="px-4 py-2 bg-cat-yellow text-onyx font-bold rounded-lg hover:bg-cat-yellow/90 transition-all flex items-center justify-center gap-2"
                        >
                            <Save size={18} />
                            Ajouter
                        </button>
                    </div>
                    <input
                        type="text"
                        placeholder="Commentaires (optionnel)"
                        value={newAction.notes || ""}
                        onChange={(e) => setNewAction({ ...newAction, notes: e.target.value || null })}
                        className="mt-3 w-full bg-black/60 border border-white/20 rounded-lg px-3 py-2 text-white placeholder:text-sand/50 focus:border-cat-yellow focus:outline-none"
                    />
                </div>

                {/* Actions Table */}
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-white/10">
                                <th className="text-left text-cat-yellow text-sm font-semibold p-3">Problème</th>
                                <th className="text-left text-cat-yellow text-sm font-semibold p-3">Owner</th>
                                <th className="text-left text-cat-yellow text-sm font-semibold p-3">Deadline</th>
                                <th className="text-left text-cat-yellow text-sm font-semibold p-3">Statut</th>
                                <th className="text-left text-cat-yellow text-sm font-semibold p-3">Commentaires</th>
                                <th className="text-left text-cat-yellow text-sm font-semibold p-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {actions.map((action) => (
                                <tr key={action.id} className="border-b border-white/5 hover:bg-white/5">
                                    <td className="text-white text-sm p-3">{action.probleme}</td>
                                    <td className="text-white text-sm p-3">{action.owner}</td>
                                    <td className="text-white text-sm p-3">{action.date_cloture_prevue || "-"}</td>
                                    <td className="p-3">
                                        <span
                                            className={`px-2 py-1 rounded text-xs font-semibold ${action.statut === "Clôturé"
                                                ? "bg-green-500/20 text-green-300"
                                                : "bg-amber-500/20 text-amber-300"
                                                }`}
                                        >
                                            {action.statut}
                                        </span>
                                    </td>
                                    <td className="text-sand/70 text-xs p-3">{action.notes || "-"}</td>
                                    <td className="p-3">
                                        <button
                                            onClick={() => handleDeleteAction(action.id!)}
                                            className="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-300 transition-all"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {actions.length === 0 && (
                        <div className="text-center py-8 text-sand/60">
                            Aucune action enregistrée. Créez-en une ci-dessus.
                        </div>
                    )}
                </div>
            </div>

            {/* CR Generation Section */}
            <div className="bg-black/60 border-2 border-cat-yellow/30 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <FileText className="text-cat-yellow" size={24} />
                        Compte Rendu
                    </h3>
                    <div className="flex gap-3">
                        <button
                            onClick={handleGenerateCR}
                            disabled={generating}
                            className="px-4 py-2 bg-cat-yellow text-onyx font-bold rounded-lg hover:bg-cat-yellow/90 transition-all disabled:opacity-50 flex items-center gap-2"
                        >
                            <FileText size={18} />
                            {generating ? "Génération..." : "Générer le CR"}
                        </button>
                        {generatedMarkdown && (
                            <button
                                onClick={() => setShowEmailModal(true)}
                                className="px-4 py-2 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 transition-all flex items-center gap-2"
                            >
                                <Send size={18} />
                                Envoyer par email
                            </button>
                        )}
                    </div>
                </div>

                <div>
                    <label className="text-sm text-sand/80 mb-2 block">Notes de discussion</label>
                    <textarea
                        value={notesDiscussion}
                        onChange={(e) => setNotesDiscussion(e.target.value)}
                        placeholder="Saisissez les notes de discussion de la réunion..."
                        className="w-full bg-onyx/60 border border-white/20 text-white rounded-lg p-3 min-h-[100px] resize-y focus:border-cat-yellow focus:outline-none"
                    />
                </div>

                {generatedMarkdown && (
                    <div className="mt-6">
                        <div className="flex justify-between items-center mb-3">
                            <h4 className="text-white font-semibold">Rapport généré</h4>
                            <button
                                onClick={handleCopyMarkdown}
                                className={`px-3 py-1.5 rounded-lg font-semibold text-sm flex items-center gap-2 transition-all ${copied
                                    ? "bg-green-600 text-white"
                                    : "bg-cat-yellow/20 text-cat-yellow hover:bg-cat-yellow/30"
                                    }`}
                            >
                                {copied ? <Check size={14} /> : <Copy size={14} />}
                                {copied ? "Copié !" : "Copier"}
                            </button>
                        </div>
                        <div className="bg-onyx/60 border border-cat-yellow/20 rounded-lg p-4">
                            <pre className="text-sm text-white whitespace-pre-wrap font-mono overflow-x-auto max-h-[400px] overflow-y-auto">
                                {generatedMarkdown}
                            </pre>
                        </div>
                    </div>
                )}
            </div>

            {/* Email Modal */}
            {showEmailModal && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-6">
                    <div className="bg-onyx border-2 border-cat-yellow/30 rounded-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                        <h3 className="text-2xl font-bold text-white mb-4">📧 Envoyer le CR</h3>

                        <div className="mb-4">
                            <p className="text-sm text-sand/80 mb-2">Destinataires ({participants.length})</p>
                            <div className="space-y-2">
                                {participants.map((p) => (
                                    <div key={p.id} className="flex items-center gap-2 text-sm">
                                        <span className="text-white font-medium">{p.name}</span>
                                        <span className="text-sand/60">({p.email})</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="mb-4">
                            <p className="text-sm text-sand/80 mb-2">Sujet</p>
                            <p className="text-white">
                                CR Meeting SEP - {new Date().toLocaleDateString("fr-FR")}
                            </p>
                        </div>

                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => setShowEmailModal(false)}
                                className="px-4 py-2 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700 transition-all"
                            >
                                Annuler
                            </button>
                            <button
                                onClick={handleSendEmail}
                                disabled={sending}
                                className="px-4 py-2 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 transition-all disabled:opacity-50 flex items-center gap-2"
                            >
                                <Send size={18} />
                                {sending ? "Envoi..." : "Envoyer"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default MeetingSEP;
