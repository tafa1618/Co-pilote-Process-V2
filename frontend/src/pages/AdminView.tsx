import { useState } from "react";
import { ArrowLeft, Upload, FileText, Trash2, Settings, Power, AlertCircle, Save } from "lucide-react";
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

interface KpiData {
    week: string;
    tech_productivity: number;
    tech_capacity: number;
    inspection_rate: number;
    llti: number;
    data_quality: number;
    service_response: number;
}

interface KpiFocusConfig {
    tech_productivity: boolean;
    tech_capacity: boolean;
    inspection_rate: boolean;
    llti: boolean;
    data_quality: boolean;
    service_response: boolean;
}

const KPI_LABELS = {
    tech_productivity: "Tech Productivity",
    tech_capacity: "Tech Capacity",
    inspection_rate: "Inspection Rate",
    llti: "LLTI",
    data_quality: "Data Quality",
    service_response: "Service Response",
};

export function AdminView({ auth, onBack }: { auth: AuthState; onBack: () => void }) {
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const [agents, setAgents] = useState<AgentConfig[]>(MOCK_AGENTS);
    const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

    // KPI Manual Entry State
    const [kpiData, setKpiData] = useState<KpiData>({
        week: new Date().toISOString().split('T')[0],
        tech_productivity: 0,
        tech_capacity: 0,
        inspection_rate: 0,
        llti: 0,
        data_quality: 0,
        service_response: 0,
    });
    const [savedKpis, setSavedKpis] = useState<KpiData[]>([]);

    // KPI Focus Selection State
    const [kpiFocus, setKpiFocus] = useState<KpiFocusConfig>({
        tech_productivity: true,
        tech_capacity: true,
        inspection_rate: true,
        llti: true,
        data_quality: true,
        service_response: true,
    });

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

    const handleSaveKpi = () => {
        if (!kpiData.week) {
            alert("Veuillez sélectionner une semaine");
            return;
        }

        // Check if KPI for this week already exists
        const existingIndex = savedKpis.findIndex(k => k.week === kpiData.week);

        if (existingIndex >= 0) {
            // Update existing
            const updated = [...savedKpis];
            updated[existingIndex] = { ...kpiData };
            setSavedKpis(updated);
            alert("KPIs mis à jour avec succès !");
        } else {
            // Add new
            setSavedKpis([...savedKpis, { ...kpiData }]);
            alert("KPIs enregistrés avec succès !");
        }

        // Reset form
        setKpiData({
            week: new Date().toISOString().split('T')[0],
            tech_productivity: 0,
            tech_capacity: 0,
            inspection_rate: 0,
            llti: 0,
            data_quality: 0,
            service_response: 0,
        });
    };

    const handleDeleteKpi = (week: string) => {
        if (confirm(`Supprimer les KPIs de la semaine du ${new Date(week).toLocaleDateString('fr-FR')} ?`)) {
            setSavedKpis(savedKpis.filter(k => k.week !== week));
        }
    };

    const handleToggleKpiFocus = (kpiKey: keyof KpiFocusConfig) => {
        setKpiFocus({ ...kpiFocus, [kpiKey]: !kpiFocus[kpiKey] });
    };

    const handleSaveKpiFocus = () => {
        // TODO: Save to backend
        const selectedCount = Object.values(kpiFocus).filter(v => v).length;
        alert(`Configuration sauvegardée ! ${selectedCount} KPI(s) sélectionné(s) pour les réunions.`);
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

            {/* KPI Manual Entry Section */}
            <div className="bg-black/60 border-2 border-cat-yellow/30 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-center gap-3 mb-6">
                    <div className="h-10 w-10 bg-cat-yellow/20 rounded-lg flex items-center justify-center">
                        <FileText className="text-cat-yellow" size={20} />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">Saisie Manuelle des KPIs</h3>
                        <p className="text-xs text-sand/60">
                            Renseignez les KPIs hebdomadaires manuellement
                        </p>
                    </div>
                </div>

                {/* KPI Entry Form */}
                <div className="bg-onyx/60 border border-cat-yellow/10 rounded-lg p-6 mb-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                        {/* Week Selection */}
                        <div className="lg:col-span-3">
                            <label className="text-sm font-semibold text-sand mb-2 block">
                                Semaine
                            </label>
                            <input
                                type="date"
                                value={kpiData.week}
                                onChange={(e) => setKpiData({ ...kpiData, week: e.target.value })}
                                className="w-full bg-black/60 border border-white/20 rounded-lg px-4 py-2 text-white focus:border-cat-yellow focus:outline-none"
                            />
                        </div>

                        {/* Tech Productivity */}
                        <div>
                            <label className="text-sm font-semibold text-sand mb-2 block">
                                Tech Productivity (%)
                            </label>
                            <input
                                type="number"
                                step="0.1"
                                value={kpiData.tech_productivity}
                                onChange={(e) => setKpiData({ ...kpiData, tech_productivity: parseFloat(e.target.value) || 0 })}
                                className="w-full bg-black/60 border border-white/20 rounded-lg px-4 py-2 text-white focus:border-cat-yellow focus:outline-none"
                                placeholder="Ex: 82.5"
                            />
                        </div>

                        {/* Tech Capacity */}
                        <div>
                            <label className="text-sm font-semibold text-sand mb-2 block">
                                Tech Capacity (h)
                            </label>
                            <input
                                type="number"
                                step="0.1"
                                value={kpiData.tech_capacity}
                                onChange={(e) => setKpiData({ ...kpiData, tech_capacity: parseFloat(e.target.value) || 0 })}
                                className="w-full bg-black/60 border border-white/20 rounded-lg px-4 py-2 text-white focus:border-cat-yellow focus:outline-none"
                                placeholder="Ex: 1250"
                            />
                        </div>

                        {/* Inspection Rate */}
                        <div>
                            <label className="text-sm font-semibold text-sand mb-2 block">
                                Inspection Rate (%)
                            </label>
                            <input
                                type="number"
                                step="0.1"
                                value={kpiData.inspection_rate}
                                onChange={(e) => setKpiData({ ...kpiData, inspection_rate: parseFloat(e.target.value) || 0 })}
                                className="w-full bg-black/60 border border-white/20 rounded-lg px-4 py-2 text-white focus:border-cat-yellow focus:outline-none"
                                placeholder="Ex: 65.2"
                            />
                        </div>

                        {/* LLTI */}
                        <div>
                            <label className="text-sm font-semibold text-sand mb-2 block">
                                LLTI (jours)
                            </label>
                            <input
                                type="number"
                                step="0.1"
                                value={kpiData.llti}
                                onChange={(e) => setKpiData({ ...kpiData, llti: parseFloat(e.target.value) || 0 })}
                                className="w-full bg-black/60 border border-white/20 rounded-lg px-4 py-2 text-white focus:border-cat-yellow focus:outline-none"
                                placeholder="Ex: 8.5"
                            />
                        </div>

                        {/* Data Quality */}
                        <div>
                            <label className="text-sm font-semibold text-sand mb-2 block">
                                Data Quality (%)
                            </label>
                            <input
                                type="number"
                                step="0.1"
                                value={kpiData.data_quality}
                                onChange={(e) => setKpiData({ ...kpiData, data_quality: parseFloat(e.target.value) || 0 })}
                                className="w-full bg-black/60 border border-white/20 rounded-lg px-4 py-2 text-white focus:border-cat-yellow focus:outline-none"
                                placeholder="Ex: 94.8"
                            />
                        </div>

                        {/* Service Response */}
                        <div>
                            <label className="text-sm font-semibold text-sand mb-2 block">
                                Service Response (h)
                            </label>
                            <input
                                type="number"
                                step="0.1"
                                value={kpiData.service_response}
                                onChange={(e) => setKpiData({ ...kpiData, service_response: parseFloat(e.target.value) || 0 })}
                                className="w-full bg-black/60 border border-white/20 rounded-lg px-4 py-2 text-white focus:border-cat-yellow focus:outline-none"
                                placeholder="Ex: 1.2"
                            />
                        </div>
                    </div>

                    <div className="flex justify-end">
                        <button
                            onClick={handleSaveKpi}
                            className="px-6 py-3 bg-cat-yellow text-onyx font-bold rounded-lg hover:bg-cat-yellow/90 transition-all flex items-center gap-2"
                        >
                            <Save size={18} />
                            Enregistrer les KPIs
                        </button>
                    </div>
                </div>

                {/* Saved KPIs List */}
                {savedKpis.length > 0 && (
                    <div>
                        <h4 className="text-sm font-semibold text-white mb-3">
                            KPIs enregistrés ({savedKpis.length})
                        </h4>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-white/10">
                                        <th className="text-left text-cat-yellow text-xs font-semibold p-3">Semaine</th>
                                        <th className="text-left text-cat-yellow text-xs font-semibold p-3">Tech Productivity (%)</th>
                                        <th className="text-left text-cat-yellow text-xs font-semibold p-3">Tech Capacity (h)</th>
                                        <th className="text-left text-cat-yellow text-xs font-semibold p-3">Inspection Rate (%)</th>
                                        <th className="text-left text-cat-yellow text-xs font-semibold p-3">LLTI (j)</th>
                                        <th className="text-left text-cat-yellow text-xs font-semibold p-3">Data Quality (%)</th>
                                        <th className="text-left text-cat-yellow text-xs font-semibold p-3">Service Response (h)</th>
                                        <th className="text-left text-cat-yellow text-xs font-semibold p-3">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {savedKpis.map((kpi) => (
                                        <tr key={kpi.week} className="border-b border-white/5 hover:bg-white/5">
                                            <td className="text-white text-sm p-3">
                                                {new Date(kpi.week).toLocaleDateString('fr-FR')}
                                            </td>
                                            <td className="text-white text-sm p-3">{kpi.tech_productivity.toFixed(1)}</td>
                                            <td className="text-white text-sm p-3">{kpi.tech_capacity.toFixed(0)}</td>
                                            <td className="text-white text-sm p-3">{kpi.inspection_rate.toFixed(1)}</td>
                                            <td className="text-white text-sm p-3">{kpi.llti.toFixed(1)}</td>
                                            <td className="text-white text-sm p-3">{kpi.data_quality.toFixed(1)}</td>
                                            <td className="text-white text-sm p-3">{kpi.service_response.toFixed(1)}</td>
                                            <td className="p-3">
                                                <button
                                                    onClick={() => handleDeleteKpi(kpi.week)}
                                                    className="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-300 transition-all"
                                                >
                                                    <Trash2 size={14} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>

            {/* KPI Focus Selection for Meetings */}
            <div className="bg-black/60 border-2 border-cat-yellow/30 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-center gap-3 mb-6">
                    <div className="h-10 w-10 bg-cat-yellow/20 rounded-lg flex items-center justify-center">
                        <Settings className="text-cat-yellow" size={20} />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">KPIs à Afficher en Réunion</h3>
                        <p className="text-xs text-sand/60">
                            Sélectionnez les KPIs pertinents pour les réunions SEP
                        </p>
                    </div>
                </div>

                <div className="bg-onyx/60 border border-cat-yellow/10 rounded-lg p-6">
                    <p className="text-sm text-sand/80 mb-4">
                        Cochez les KPIs que vous souhaitez afficher dans la vue "Meeting SEP" :
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                        {(Object.keys(kpiFocus) as Array<keyof KpiFocusConfig>).map((kpiKey) => (
                            <label
                                key={kpiKey}
                                className={`flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${kpiFocus[kpiKey]
                                        ? "border-cat-yellow bg-cat-yellow/10"
                                        : "border-white/10 bg-onyx/40 hover:border-white/30"
                                    }`}
                            >
                                <input
                                    type="checkbox"
                                    checked={kpiFocus[kpiKey]}
                                    onChange={() => handleToggleKpiFocus(kpiKey)}
                                    className="w-5 h-5 accent-cat-yellow cursor-pointer"
                                />
                                <span className={`font-medium ${kpiFocus[kpiKey] ? "text-white" : "text-sand/70"}`}>
                                    {KPI_LABELS[kpiKey]}
                                </span>
                            </label>
                        ))}
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-white/10">
                        <p className="text-sm text-sand/60">
                            {Object.values(kpiFocus).filter(v => v).length} / {Object.keys(kpiFocus).length} KPIs sélectionnés
                        </p>
                        <button
                            onClick={handleSaveKpiFocus}
                            className="px-6 py-3 bg-cat-yellow text-onyx font-bold rounded-lg hover:bg-cat-yellow/90 transition-all flex items-center gap-2"
                        >
                            <Save size={18} />
                            Sauvegarder la sélection
                        </button>
                    </div>
                </div>
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
