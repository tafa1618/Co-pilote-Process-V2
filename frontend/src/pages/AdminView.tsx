import { useState } from "react";
import { ArrowLeft, Upload, FileText, Trash2, Settings, Power, AlertCircle } from "lucide-react";
import type { AuthState } from "../types";

interface UploadedFile {
    id: string;
    name: string;
    type: string;
    size: number;
    uploadedAt: string;
}

interface AgentConfig {
    id: string;
    name: string;
    description: string;
    enabled: boolean;
    thresholds: {
        [key: string]: number;
    };
    frequency: string;
    monitoredKpis: string[];
}

const MOCK_AGENTS: AgentConfig[] = [
    {
        id: "performance_watcher",
        name: "Performance Watcher",
        description: "Surveille les baisses de productivité et détecte les patterns récurrents",
        enabled: true,
        thresholds: {
            productivity_min: 78,
            alert_threshold: 68,
        },
        frequency: "daily",
        monitoredKpis: ["tech_productivity", "tech_capacity"],
    },
    {
        id: "quality_guardian",
        name: "Quality Guardian",
        description: "Analyse la qualité des données et le taux d'inspection",
        enabled: true,
        thresholds: {
            inspection_min: 50,
            data_quality_min: 90,
        },
        frequency: "weekly",
        monitoredKpis: ["inspection_rate", "data_quality"],
    },
    {
        id: "process_optimizer",
        name: "Process Optimizer",
        description: "Identifie les goulots d'étranglement dans les processus",
        enabled: false,
        thresholds: {
            llti_max: 12,
            response_time_max: 2,
        },
        frequency: "weekly",
        monitoredKpis: ["llti", "service_response"],
    },
];

export function AdminView({ auth, onBack }: { auth: AuthState; onBack: () => void }) {
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const [agents, setAgents] = useState<AgentConfig[]>(MOCK_AGENTS);
    const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const files = Array.from(e.target.files);
            handleFiles(files);
        }
    };

    const handleFiles = (files: File[]) => {
        const validTypes = [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel",
            "text/csv",
        ];

        files.forEach((file) => {
            if (!validTypes.includes(file.type)) {
                alert(`Type de fichier non supporté: ${file.name}`);
                return;
            }

            const newFile: UploadedFile = {
                id: Math.random().toString(36).substr(2, 9),
                name: file.name,
                type: file.type.includes("csv") ? "CSV" : "Excel",
                size: file.size,
                uploadedAt: new Date().toISOString(),
            };

            setUploadedFiles((prev) => [...prev, newFile]);
        });
    };

    const handleDeleteFile = (id: string) => {
        if (confirm("Êtes-vous sûr de vouloir supprimer ce fichier ?")) {
            setUploadedFiles((prev) => prev.filter((f) => f.id !== id));
        }
    };

    const toggleAgent = (agentId: string) => {
        setAgents((prev) =>
            prev.map((agent) =>
                agent.id === agentId ? { ...agent, enabled: !agent.enabled } : agent
            )
        );
    };

    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
        return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    };

    const selectedAgentData = agents.find((a) => a.id === selectedAgent);

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
                    <h2 className="text-3xl font-bold text-white">Administration</h2>
                    <p className="text-sand/60 text-sm">
                        Gestion des fichiers et configuration des agents
                    </p>
                </div>
                <div className="text-right">
                    <p className="text-xs text-sand/60">Connecté en tant que</p>
                    <p className="text-sm font-semibold text-cat-yellow">{auth.user?.email}</p>
                </div>
            </div>

            {/* File Upload Section */}
            <div className="bg-black/60 border-2 border-cat-yellow/30 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-center gap-3 mb-6">
                    <div className="h-10 w-10 bg-cat-yellow/20 rounded-lg flex items-center justify-center">
                        <Upload className="text-cat-yellow" size={20} />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">Gestion des Fichiers</h3>
                        <p className="text-xs text-sand/60">
                            Uploadez des fichiers Excel ou CSV pour alimenter les données SEP
                        </p>
                    </div>
                </div>

                {/* Drag & Drop Zone */}
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${isDragging
                            ? "border-cat-yellow bg-cat-yellow/10"
                            : "border-white/20 hover:border-cat-yellow/50"
                        }`}
                >
                    <Upload className="mx-auto mb-4 text-cat-yellow" size={48} />
                    <p className="text-white font-semibold mb-2">
                        Glissez-déposez vos fichiers ici
                    </p>
                    <p className="text-sand/60 text-sm mb-4">ou</p>
                    <label className="inline-block px-6 py-3 bg-cat-yellow text-onyx font-bold rounded-lg cursor-pointer hover:bg-cat-yellow/90 transition-all">
                        Parcourir les fichiers
                        <input
                            type="file"
                            multiple
                            accept=".xlsx,.xls,.csv"
                            onChange={handleFileInput}
                            className="hidden"
                        />
                    </label>
                    <p className="text-xs text-sand/60 mt-4">
                        Formats acceptés : Excel (.xlsx, .xls), CSV (.csv)
                    </p>
                </div>

                {/* Uploaded Files List */}
                {uploadedFiles.length > 0 && (
                    <div className="mt-6">
                        <h4 className="text-sm font-semibold text-white mb-3">
                            Fichiers uploadés ({uploadedFiles.length})
                        </h4>
                        <div className="space-y-2">
                            {uploadedFiles.map((file) => (
                                <div
                                    key={file.id}
                                    className="flex items-center justify-between bg-onyx/60 border border-white/10 rounded-lg p-3 hover:border-cat-yellow/30 transition-all"
                                >
                                    <div className="flex items-center gap-3">
                                        <FileText className="text-cat-yellow" size={20} />
                                        <div>
                                            <p className="text-white text-sm font-medium">{file.name}</p>
                                            <p className="text-sand/60 text-xs">
                                                {file.type} • {formatFileSize(file.size)} •{" "}
                                                {new Date(file.uploadedAt).toLocaleString("fr-FR")}
                                            </p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => handleDeleteFile(file.id)}
                                        className="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-300 transition-all"
                                        title="Supprimer"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Agent Configuration Section */}
            <div className="bg-black/60 border-2 border-cat-yellow/30 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-center gap-3 mb-6">
                    <div className="h-10 w-10 bg-cat-yellow/20 rounded-lg flex items-center justify-center">
                        <Settings className="text-cat-yellow" size={20} />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">Configuration des Agents</h3>
                        <p className="text-xs text-sand/60">
                            Gérez les agents d'analyse et leurs paramètres
                        </p>
                    </div>
                </div>

                {/* Agents List */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {agents.map((agent) => (
                        <div
                            key={agent.id}
                            onClick={() => setSelectedAgent(agent.id)}
                            className={`bg-onyx/60 border-2 rounded-lg p-4 cursor-pointer transition-all ${selectedAgent === agent.id
                                    ? "border-cat-yellow"
                                    : "border-white/10 hover:border-cat-yellow/50"
                                }`}
                        >
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <AlertCircle
                                        className={agent.enabled ? "text-green-400" : "text-gray-400"}
                                        size={20}
                                    />
                                    <h4 className="text-white font-bold text-sm">{agent.name}</h4>
                                </div>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        toggleAgent(agent.id);
                                    }}
                                    className={`p-1.5 rounded-lg transition-all ${agent.enabled
                                            ? "bg-green-500/20 text-green-300"
                                            : "bg-gray-500/20 text-gray-400"
                                        }`}
                                    title={agent.enabled ? "Désactiver" : "Activer"}
                                >
                                    <Power size={14} />
                                </button>
                            </div>
                            <p className="text-sand/70 text-xs mb-3">{agent.description}</p>
                            <div className="flex items-center justify-between text-xs">
                                <span className="text-sand/60">Fréquence: {agent.frequency}</span>
                                <span
                                    className={`px-2 py-1 rounded ${agent.enabled
                                            ? "bg-green-500/20 text-green-300"
                                            : "bg-gray-500/20 text-gray-400"
                                        }`}
                                >
                                    {agent.enabled ? "Actif" : "Inactif"}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Agent Configuration Panel */}
                {selectedAgentData && (
                    <div className="mt-6 bg-onyx/60 border border-cat-yellow/30 rounded-lg p-6">
                        <h4 className="text-lg font-bold text-white mb-4">
                            Configuration : {selectedAgentData.name}
                        </h4>

                        <div className="space-y-4">
                            {/* Thresholds */}
                            <div>
                                <label className="text-sm font-semibold text-sand mb-2 block">
                                    Seuils d'alerte
                                </label>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    {Object.entries(selectedAgentData.thresholds).map(([key, value]) => (
                                        <div key={key}>
                                            <label className="text-xs text-sand/60 mb-1 block capitalize">
                                                {key.replace(/_/g, " ")}
                                            </label>
                                            <input
                                                type="number"
                                                value={value}
                                                onChange={(e) => {
                                                    const newValue = parseFloat(e.target.value);
                                                    setAgents((prev) =>
                                                        prev.map((agent) =>
                                                            agent.id === selectedAgentData.id
                                                                ? {
                                                                    ...agent,
                                                                    thresholds: { ...agent.thresholds, [key]: newValue },
                                                                }
                                                                : agent
                                                        )
                                                    );
                                                }}
                                                className="w-full bg-black/60 border border-white/20 rounded-lg px-3 py-2 text-white focus:border-cat-yellow focus:outline-none"
                                            />
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Frequency */}
                            <div>
                                <label className="text-sm font-semibold text-sand mb-2 block">
                                    Fréquence d'analyse
                                </label>
                                <select
                                    value={selectedAgentData.frequency}
                                    onChange={(e) => {
                                        setAgents((prev) =>
                                            prev.map((agent) =>
                                                agent.id === selectedAgentData.id
                                                    ? { ...agent, frequency: e.target.value }
                                                    : agent
                                            )
                                        );
                                    }}
                                    className="w-full bg-black/60 border border-white/20 rounded-lg px-3 py-2 text-white focus:border-cat-yellow focus:outline-none"
                                >
                                    <option value="hourly">Toutes les heures</option>
                                    <option value="daily">Quotidien</option>
                                    <option value="weekly">Hebdomadaire</option>
                                    <option value="monthly">Mensuel</option>
                                </select>
                            </div>

                            {/* Monitored KPIs */}
                            <div>
                                <label className="text-sm font-semibold text-sand mb-2 block">
                                    KPIs surveillés
                                </label>
                                <div className="flex flex-wrap gap-2">
                                    {selectedAgentData.monitoredKpis.map((kpi) => (
                                        <span
                                            key={kpi}
                                            className="px-3 py-1 bg-cat-yellow/20 text-cat-yellow rounded-full text-xs font-medium"
                                        >
                                            {kpi}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Save Button */}
                            <div className="flex justify-end pt-4">
                                <button className="px-6 py-3 bg-cat-yellow text-onyx font-bold rounded-lg hover:bg-cat-yellow/90 transition-all">
                                    Sauvegarder la configuration
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default AdminView;
