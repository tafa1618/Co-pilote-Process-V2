import { useState, useEffect } from "react";
import { Calculator, AlertTriangle, TrendingUp, RefreshCw, Trophy } from "lucide-react";

// --- Types & Constants ---

interface KpiConfig {
    id: string;
    label: string;
    weight: number; // percentage (e.g., 12 for 12%)
    targets: {
        emerging: number; // 1 point
        advanced: number; // 2 points
        excellent: number; // 3 points
    };
    inverse?: boolean; // True if lower is better (e.g., RIF, LLTI)
    unit: string;
}

const FOUNDATION_KPIS: KpiConfig[] = [
    { id: "service_rif", label: "Service RIF", weight: 12, targets: { emerging: 1.3, advanced: 0.8, excellent: 0.5 }, inverse: true, unit: "" },
    { id: "tech_productivity", label: "Tech Productivity", weight: 6, targets: { emerging: 78, advanced: 82, excellent: 85 }, unit: "%" },
    { id: "tech_capacity", label: "Tech Capacity", weight: 6, targets: { emerging: 94, advanced: 96, excellent: 98 }, unit: "%" },
    { id: "llti", label: "LLTI", weight: 5, targets: { emerging: 17, advanced: 12, excellent: 7 }, inverse: true, unit: "j" },
    { id: "tech_capability", label: "Tech Capability (TCDPA)", weight: 6, targets: { emerging: 60, advanced: 85, excellent: 95 }, unit: "%" },
    { id: "service_data_quality", label: "Service Data Quality", weight: 5, targets: { emerging: 85, advanced: 90, excellent: 95 }, unit: "%" },
];

const GROWTH_KPIS: KpiConfig[] = [
    { id: "service_response", label: "Service Response", weight: 10, targets: { emerging: 75, advanced: 85, excellent: 95 }, unit: "%" },
    { id: "cva_fulfillment", label: "CVA Fulfillment", weight: 12, targets: { emerging: 70, advanced: 80, excellent: 90 }, unit: "%" },
    { id: "inspection_rate", label: "Inspection Rate", weight: 12, targets: { emerging: 50, advanced: 65, excellent: 80 }, unit: "%" },
    { id: "remote_service", label: "Remote Service", weight: 8, targets: { emerging: 40, advanced: 60, excellent: 80 }, unit: "%" },
    { id: "cva_pm_coverage", label: "CVA PM Coverage", weight: 10, targets: { emerging: 60, advanced: 75, excellent: 90 }, unit: "%" },
    { id: "cma_recommendation", label: "CMA Recommendation", weight: 8, targets: { emerging: 50, advanced: 70, excellent: 90 }, unit: "%" },
];

interface SimulationResult {
    foundationScore: number; // /40
    growthScore: number;     // /60
    totalScore: number;      // /100
    level: "Gold" | "Silver" | "Bronze" | "Non-Scoring";
    downgraded: boolean;
    details: Record<string, { points: number; score: number; level: string }>;
}

export function SepSimulator() {
    // --- State ---
    const [inputs, setInputs] = useState<Record<string, number>>({
        service_rif: 1.0, tech_productivity: 80, tech_capacity: 95, llti: 10, tech_capability: 70, service_data_quality: 88,
        service_response: 80, cva_fulfillment: 75, inspection_rate: 60, remote_service: 50, cva_pm_coverage: 70, cma_recommendation: 60
    });
    const [result, setResult] = useState<SimulationResult | null>(null);

    // --- Calculation Logic ---
    const calculateScore = () => {
        let foundScore = 0;
        let growthScore = 0;
        const details: any = {};

        // Helper to calc points
        const calcPoints = (val: number, cfg: KpiConfig) => {
            if (cfg.inverse) {
                if (val <= cfg.targets.excellent) return 3;
                if (val <= cfg.targets.advanced) return 2;
                if (val <= cfg.targets.emerging) return 1;
                return 0;
            } else {
                if (val >= cfg.targets.excellent) return 3;
                if (val >= cfg.targets.advanced) return 2;
                if (val >= cfg.targets.emerging) return 1;
                return 0;
            }
        };

        // Foundation
        FOUNDATION_KPIS.forEach(kpi => {
            const points = calcPoints(inputs[kpi.id], kpi);
            const score = (points / 3) * kpi.weight;
            foundScore += score;
            details[kpi.id] = { points, score, level: points === 3 ? "Exec" : points === 2 ? "Adv" : points === 1 ? "Emerg" : "-" };
        });

        // Growth
        GROWTH_KPIS.forEach(kpi => {
            const points = calcPoints(inputs[kpi.id], kpi);
            const score = (points / 3) * kpi.weight;
            growthScore += score;
            details[kpi.id] = { points, score, level: points === 3 ? "Exec" : points === 2 ? "Adv" : points === 1 ? "Emerg" : "-" };
        });

        const total = foundScore + growthScore;

        // Level Logic with Downgrade Rule
        let level: "Gold" | "Silver" | "Bronze" | "Non-Scoring" = "Non-Scoring";
        let downgraded = false;

        // Base level
        if (total >= 75) level = "Gold";
        else if (total >= 60) level = "Silver";
        else if (total >= 40) level = "Bronze";

        // Check category minimums
        // Gold requires all cats > Silver (60% of their weight)
        // Silver requires all cats > Bronze (40% of their weight)

        const foundPct = (foundScore / 40) * 100;
        const growthPct = (growthScore / 60) * 100;

        if (level === "Gold") {
            if (foundPct < 60 || growthPct < 60) {
                level = "Silver";
                downgraded = true;
            }
        }

        if (level === "Silver" && !downgraded) { // check if not already downgraded
            if (foundPct < 40 || growthPct < 40) {
                level = "Bronze";
                downgraded = true;
            }
        }

        setResult({
            foundationScore: foundScore,
            growthScore: growthScore,
            totalScore: total,
            level,
            downgraded,
            details
        });
    };

    useEffect(() => {
        calculateScore();
    }, [inputs]);

    const handleChange = (id: string, val: string) => {
        setInputs(prev => ({ ...prev, [id]: parseFloat(val) || 0 }));
    };

    // --- Render ---
    const getLevelColor = (l: string) => {
        switch (l) {
            case "Gold": return "text-yellow-400 border-yellow-400";
            case "Silver": return "text-gray-300 border-gray-300";
            case "Bronze": return "text-amber-600 border-amber-600";
            default: return "text-red-500 border-red-500";
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
            {/* INPUTS COLUMNS */}
            <div className="lg:col-span-2 space-y-6 overflow-y-auto pr-2 max-h-[80vh]">

                {/* Foundation */}
                <div className="bg-black/40 border border-white/10 rounded-xl p-5">
                    <h3 className="text-lg font-bold text-cat-yellow mb-4 flex items-center gap-2">
                        <TrendingUp size={20} /> Foundation of Operations (40%)
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {FOUNDATION_KPIS.map(kpi => (
                            <div key={kpi.id} className="bg-onyx/40 p-3 rounded-lg border border-white/5">
                                <label className="text-xs text-sand/70 block mb-1 flex justify-between">
                                    {kpi.label}
                                    <span className="text-cat-yellow">{inputs[kpi.id]}{kpi.unit}</span>
                                </label>
                                <input
                                    type="range"
                                    min={kpi.inverse ? 0 : 0}
                                    max={kpi.inverse ? 20 : 120}
                                    step={kpi.inverse ? 0.1 : 1}
                                    value={inputs[kpi.id]}
                                    onChange={(e) => handleChange(kpi.id, e.target.value)}
                                    className="w-full accent-cat-yellow mb-2 cursor-pointer"
                                />
                                <div className="flex justify-between text-[10px] text-zinc-500 font-mono">
                                    <span>{kpi.inverse ? '>' + kpi.targets.emerging : '<' + kpi.targets.emerging}</span>
                                    <span>{kpi.inverse ? kpi.targets.advanced : kpi.targets.advanced}</span>
                                    <span>{kpi.inverse ? '<' + kpi.targets.excellent : '>' + kpi.targets.excellent}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Growth */}
                <div className="bg-black/40 border border-white/10 rounded-xl p-5">
                    <h3 className="text-lg font-bold text-blue-400 mb-4 flex items-center gap-2">
                        <TrendingUp size={20} /> Services Growth (60%)
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {GROWTH_KPIS.map(kpi => (
                            <div key={kpi.id} className="bg-onyx/40 p-3 rounded-lg border border-white/5">
                                <label className="text-xs text-sand/70 block mb-1 flex justify-between">
                                    {kpi.label}
                                    <span className="text-blue-300">{inputs[kpi.id]}{kpi.unit}</span>
                                </label>
                                <input
                                    type="range"
                                    min="0" max="100"
                                    value={inputs[kpi.id]}
                                    onChange={(e) => handleChange(kpi.id, e.target.value)}
                                    className="w-full accent-blue-500 mb-2 cursor-pointer"
                                />
                                <div className="flex justify-between text-[10px] text-zinc-500 font-mono">
                                    <span>{'<' + kpi.targets.emerging}</span>
                                    <span>{kpi.targets.advanced}</span>
                                    <span>{'>' + kpi.targets.excellent}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* RESULTS COLUMN */}
            <div className="bg-onyx border-2 border-cat-yellow/20 rounded-xl p-6 flex flex-col gap-6 sticky top-6 h-fit">
                <div className="flex items-center gap-2 text-cat-yellow mb-2">
                    <Calculator />
                    <h2 className="text-2xl font-bold text-white">Résultat Simulé</h2>
                </div>

                {/* Score Badge */}
                <div className={`border-4 rounded-full w-40 h-40 mx-auto flex flex-col items-center justify-center bg-black/50 ${getLevelColor(result?.level || "")}`}>
                    <Trophy size={32} className="mb-2" />
                    <span className="text-3xl font-black">{result?.totalScore.toFixed(1)}%</span>
                    <span className="text-sm font-bold uppercase tracking-wider">{result?.level}</span>
                </div>

                {/* Alert Downgrade */}
                {result?.downgraded && (
                    <div className="bg-red-500/10 border border-red-500/50 p-3 rounded-lg flex gap-3 items-start">
                        <AlertTriangle className="text-red-400 shrink-0" size={18} />
                        <div className="text-xs text-red-200">
                            <strong>Niveau abaissé !</strong> Une des catégories n'a pas atteint le minimum requis pour le niveau supérieur.
                        </div>
                    </div>
                )}

                {/* Categories Breakdown */}
                <div className="space-y-4">
                    <div>
                        <div className="flex justify-between text-sm mb-1">
                            <span className="text-sand">Foundation (max 40)</span>
                            <span className="font-bold text-white">{result?.foundationScore.toFixed(1)}</span>
                        </div>
                        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div className="h-full bg-cat-yellow transition-all duration-500" style={{ width: `${(result?.foundationScore || 0) / 40 * 100}%` }}></div>
                        </div>
                    </div>

                    <div>
                        <div className="flex justify-between text-sm mb-1">
                            <span className="text-sand">Growth (max 60)</span>
                            <span className="font-bold text-white">{result?.growthScore.toFixed(1)}</span>
                        </div>
                        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div className="h-full bg-blue-500 transition-all duration-500" style={{ width: `${(result?.growthScore || 0) / 60 * 100}%` }}></div>
                        </div>
                    </div>
                </div>

                <div className="mt-auto pt-6 border-t border-white/10">
                    <button
                        onClick={() => calculateScore()} // actually state updates trigger calc, this could reset or save
                        className="w-full py-3 bg-white/5 hover:bg-white/10 text-white rounded-lg flex items-center justify-center gap-2 transition-all font-semibold"
                    >
                        <RefreshCw size={18} /> Recalculer / Reset
                    </button>
                    <p className="text-[10px] text-center text-zinc-600 mt-2">
                        Basé sur les règles officielles SEP 2025 Zone Afrique
                    </p>
                </div>
            </div>
        </div>
    );
}
