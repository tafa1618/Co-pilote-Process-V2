import React, { useState, useEffect } from "react";
import { Bot, AlertTriangle, CheckCircle, Info, ChevronDown, ChevronUp } from "lucide-react";

interface Insight {
    id: number;
    agent: string;
    type: "warning" | "success" | "info";
    message: string;
    details: string;
}

interface Action {
    id: number;
    title: string;
    priority: "High" | "Medium" | "Low";
    status: string;
    owner: string;
    description: string;
}

interface AgentData {
    insights: Insight[];
    actions: Action[];
}

interface Props {
    isAdmin: boolean;
    data: AgentData | null;
    loading: boolean;
}

const AgentInsightsPanel: React.FC<Props> = ({ isAdmin, data, loading }) => {
    const [isOpen, setIsOpen] = useState(false);

    if (!isAdmin) return null;

    return (
        <div className="fixed bottom-4 right-4 z-50 flex flex-col items-end space-y-2">
            {isOpen && (
                <div className="w-96 rounded-2xl border-2 border-cat-yellow bg-onyx/95 p-4 shadow-2xl backdrop-blur-xl text-sand transition-all animate-in slide-in-from-bottom-10 fade-in duration-300">
                    <div className="mb-4 flex items-center justify-between border-b border-white/10 pb-2">
                        <div className="flex items-center gap-2">
                            <Bot className="text-cat-yellow" size={20} />
                            <h3 className="font-bold text-white uppercase tracking-wider text-sm">Agent Intel</h3>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="text-sand/50 hover:text-white">
                            <ChevronDown size={18} />
                        </button>
                    </div>

                    <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2 custom-scrollbar">
                        {loading ? (
                            <div className="flex justify-center p-4">
                                <div className="h-6 w-6 animate-spin rounded-full border-2 border-cat-yellow border-t-transparent"></div>
                            </div>
                        ) : data ? (
                            <>
                                <div className="space-y-3">
                                    <h4 className="text-xs font-bold uppercase text-sand/50">Insights Détectés</h4>
                                    {data.insights.map((insight) => (
                                        <div key={insight.id} className="rounded-lg bg-white/5 p-3 border-l-2 border-transparent hover:bg-white/10 transition-colors"
                                            style={{ borderLeftColor: insight.type === 'warning' ? '#ef4444' : insight.type === 'success' ? '#10b981' : '#3b82f6' }}>
                                            <div className="flex items-start gap-2 mb-1">
                                                {insight.type === 'warning' && <AlertTriangle size={14} className="text-red-500 mt-1" />}
                                                {insight.type === 'success' && <CheckCircle size={14} className="text-emerald-500 mt-1" />}
                                                {insight.type === 'info' && <Info size={14} className="text-blue-500 mt-1" />}
                                                <span className="text-xs font-mono text-cat-yellow bg-black/40 px-1.5 rounded">{insight.agent}</span>
                                            </div>
                                            <p className="text-sm font-medium text-white leading-tight mb-1">{insight.message}</p>
                                            <p className="text-xs text-sand/70">{insight.details}</p>
                                        </div>
                                    ))}
                                </div>

                                <div className="space-y-3 pt-2 border-t border-white/10">
                                    <h4 className="text-xs font-bold uppercase text-sand/50">Actions Suggérées</h4>
                                    {data.actions.map((action) => (
                                        <div key={action.id} className="rounded-lg border border-white/10 bg-black/40 p-3">
                                            <div className="flex justify-between items-start mb-2">
                                                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${action.priority === 'High' ? 'bg-red-500/20 text-red-300' : 'bg-cat-yellow/20 text-cat-yellow'
                                                    }`}>{action.priority}</span>
                                                <span className="text-[10px] text-sand/50">{action.owner}</span>
                                            </div>
                                            <h5 className="text-sm font-bold text-white mb-1">{action.title}</h5>
                                            <p className="text-xs text-sand/70">{action.description}</p>
                                        </div>
                                    ))}
                                </div>
                            </>
                        ) : null}
                    </div>
                </div>
            )}

            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`flex h-12 w-12 items-center justify-center rounded-full shadow-lg transition-all hover:scale-110 ${isOpen ? "bg-onyx border-2 border-cat-yellow text-cat-yellow" : "bg-cat-yellow text-onyx hover:bg-white hover:text-onyx"
                    }`}
                title="Admin Agents Insights"
            >
                <Bot size={24} />
            </button>
        </div>
    );
};

export default AgentInsightsPanel;
