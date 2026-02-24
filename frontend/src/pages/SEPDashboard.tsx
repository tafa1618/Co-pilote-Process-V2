import React, { useState, useEffect } from 'react';
import KPICard from '../components/KPICard';
import KPIDetailModal from '../components/KPIDetailModal';
import { Bot, Building } from 'lucide-react';
import { BACKEND_URL } from '../config/constants';

interface SEPDashboardProps {
    user: any;
    isAdmin: boolean;
}

const SEPDashboard: React.FC<SEPDashboardProps> = ({ user, isAdmin }) => {
    const [sepData, setSepData] = useState<any>(null);
    const [insights, setInsights] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [selectedKPI, setSelectedKPI] = useState<string | null>(null);

    useEffect(() => {
        // Fetch SEP KPIs
        Promise.all([
            fetch(`${BACKEND_URL}/api/sep/kpis`).then(res => res.json()),
            fetch(`${BACKEND_URL}/api/sep/insights`).then(res => res.json())
        ])
            .then(([kpisData, insightsData]) => {
                setSepData(kpisData);
                setInsights(insightsData);
            })
            .catch(err => console.error('Failed to load SEP data', err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-onyx flex items-center justify-center">
                <div className="text-center">
                    <div className="h-12 w-12 animate-spin rounded-full border-4 border-cat-yellow border-t-transparent mx-auto mb-4"></div>
                    <p className="text-sand">Chargement des KPIs SEP...</p>
                </div>
            </div>
        );
    }

    if (!sepData) {
        return (
            <div className="min-h-screen bg-onyx flex items-center justify-center">
                <p className="text-red-500">Erreur de chargement des données</p>
            </div>
        );
    }

    const foundationKPIs = Object.values(sepData.categories.foundation_ops.kpis);
    const servicesKPIs = Object.values(sepData.categories.services_growth.kpis);

    return (
        <div className="min-h-screen bg-gradient-to-br from-onyx via-black to-onyx text-sand">
            {/* Hero Header with Neemba Branding */}
            <div className="relative overflow-hidden bg-gradient-to-r from-onyx to-black border-b-4 border-cat-yellow">
                <div className="absolute inset-0 opacity-10">
                    <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0ZGQ0QxMSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-20"></div>
                </div>

                <div className="relative z-10 p-8">
                    <div className="max-w-7xl mx-auto">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-4">
                                <div className="h-16 w-16 bg-cat-yellow rounded-xl flex items-center justify-center shadow-lg">
                                    <Building className="text-onyx" size={32} />
                                </div>
                                <div>
                                    <h1 className="text-5xl font-black text-white mb-1">
                                        NEEMBA <span className="text-cat-yellow">CAT</span>
                                    </h1>
                                    <p className="text-sm text-cat-yellow/80 uppercase tracking-widest font-semibold">
                                        +100 ans de confiance • Concessionnaire Caterpillar
                                    </p>
                                </div>
                            </div>

                            <div className="text-right bg-black/40 backdrop-blur-sm rounded-xl p-6 border-2 border-cat-yellow/30">
                                <div className="text-xs text-sand/60 mb-1 uppercase tracking-wider">Score Global SEP</div>
                                <div className="text-6xl font-black text-cat-yellow mb-1">
                                    {sepData.overall_score}%
                                </div>
                                <div className="text-xl font-bold text-cat-yellow mb-2">
                                    {sepData.performance_level}
                                </div>
                                <div className="text-xs text-sand/70 italic">
                                    Des solutions conçues pour performer
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-2 mb-4">
                            <span className="h-1 w-12 bg-cat-yellow"></span>
                            <h2 className="text-2xl font-bold text-white">
                                Digital Twin - Service Excellence Program
                            </h2>
                            <span className="text-sand/50">•</span>
                            <span className="text-sand/70">{sepData.period}</span>
                        </div>

                        {/* Category Scores */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-black/60 backdrop-blur-sm border-2 border-white/10 rounded-xl p-5 hover:border-cat-yellow/50 transition-all">
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="text-2xl">⚙️</span>
                                    <div className="text-sm text-sand/60 uppercase tracking-wider font-semibold">
                                        Foundation of Operations
                                    </div>
                                </div>
                                <div className="flex items-baseline gap-3">
                                    <span className="text-4xl font-black text-white">
                                        {sepData.categories.foundation_ops.score}%
                                    </span>
                                    <span className="text-sm text-sand/60">
                                        (Poids: {sepData.categories.foundation_ops.weight}%)
                                    </span>
                                </div>
                                <div className="text-sm font-bold text-cat-yellow mt-2">
                                    {sepData.categories.foundation_ops.performance_level}
                                </div>
                            </div>

                            <div className="bg-black/60 backdrop-blur-sm border-2 border-white/10 rounded-xl p-5 hover:border-cat-yellow/50 transition-all">
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="text-2xl">📈</span>
                                    <div className="text-sm text-sand/60 uppercase tracking-wider font-semibold">
                                        Services Growth
                                    </div>
                                </div>
                                <div className="flex items-baseline gap-3">
                                    <span className="text-4xl font-black text-white">
                                        {sepData.categories.services_growth.score}%
                                    </span>
                                    <span className="text-sm text-sand/60">
                                        (Poids: {sepData.categories.services_growth.weight}%)
                                    </span>
                                </div>
                                <div className="text-sm font-bold text-cat-yellow mt-2">
                                    {sepData.categories.services_growth.performance_level}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto p-6">
                {/* Foundation of Operations KPIs */}
                <div className="mb-10">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="h-10 w-10 bg-cat-yellow/20 rounded-lg flex items-center justify-center">
                            <span className="text-2xl">⚙️</span>
                        </div>
                        <h2 className="text-3xl font-black text-white">
                            Foundation of Operations
                        </h2>
                        <div className="h-1 flex-1 bg-gradient-to-r from-cat-yellow/50 to-transparent"></div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {foundationKPIs.map((kpi: any) => (
                            <KPICard
                                key={kpi.name}
                                {...kpi}
                                onClick={() => setSelectedKPI(kpi.name)}
                            />
                        ))}
                    </div>
                </div>

                {/* Services Growth KPIs */}
                <div className="mb-10">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="h-10 w-10 bg-cat-yellow/20 rounded-lg flex items-center justify-center">
                            <span className="text-2xl">📈</span>
                        </div>
                        <h2 className="text-3xl font-black text-white">
                            Services Growth
                        </h2>
                        <div className="h-1 flex-1 bg-gradient-to-r from-cat-yellow/50 to-transparent"></div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {servicesKPIs.map((kpi: any) => (
                            <KPICard
                                key={kpi.name}
                                {...kpi}
                                onClick={() => setSelectedKPI(kpi.name)}
                            />
                        ))}
                    </div>
                </div>

                {/* Agent Insights (Admin Only) */}
                {isAdmin && insights && (
                    <div className="mb-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="h-10 w-10 bg-cat-yellow/20 rounded-lg flex items-center justify-center">
                                <Bot className="text-cat-yellow" size={24} />
                            </div>
                            <h2 className="text-3xl font-black text-white">
                                Agent Insights
                            </h2>
                            <span className="text-xs bg-cat-yellow/20 text-cat-yellow px-3 py-1 rounded-full font-bold uppercase">
                                Admin Only
                            </span>
                            <div className="h-1 flex-1 bg-gradient-to-r from-cat-yellow/50 to-transparent"></div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Insights */}
                            <div className="space-y-4">
                                <h3 className="text-sm font-bold uppercase text-sand/50 mb-3 flex items-center gap-2">
                                    <span className="h-2 w-2 bg-cat-yellow rounded-full"></span>
                                    Détections
                                </h3>
                                {insights.insights.map((insight: any) => (
                                    <div
                                        key={insight.id}
                                        className="bg-black/60 backdrop-blur-sm border-l-4 rounded-xl p-5 hover:bg-black/80 transition-all"
                                        style={{
                                            borderLeftColor:
                                                insight.type === 'warning'
                                                    ? '#ef4444'
                                                    : insight.type === 'success'
                                                        ? '#10b981'
                                                        : '#3b82f6'
                                        }}
                                    >
                                        <div className="flex items-start gap-2 mb-3">
                                            <span className="text-xs font-mono bg-black/60 px-3 py-1 rounded-full text-cat-yellow border border-cat-yellow/30">
                                                {insight.agent}
                                            </span>
                                            <span
                                                className={`text-xs px-3 py-1 rounded-full font-bold ${insight.priority === 'HIGH'
                                                    ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                                                    : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
                                                    }`}
                                            >
                                                {insight.priority}
                                            </span>
                                        </div>
                                        <p className="text-sm font-semibold text-white mb-2">
                                            {insight.message}
                                        </p>
                                        <p className="text-xs text-sand/70 leading-relaxed">{insight.details}</p>
                                    </div>
                                ))}
                            </div>

                            {/* Actions */}
                            <div className="space-y-4">
                                <h3 className="text-sm font-bold uppercase text-sand/50 mb-3 flex items-center gap-2">
                                    <span className="h-2 w-2 bg-cat-yellow rounded-full"></span>
                                    Actions Suggérées
                                </h3>
                                {insights.actions.map((action: any) => (
                                    <div
                                        key={action.id}
                                        className="bg-black/60 backdrop-blur-sm border-2 border-white/10 rounded-xl p-5 hover:border-cat-yellow/50 transition-all"
                                    >
                                        <div className="flex justify-between items-start mb-3">
                                            <span
                                                className={`text-xs px-3 py-1 rounded-full font-bold ${action.priority === 'HIGH'
                                                    ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                                                    : 'bg-cat-yellow/20 text-cat-yellow border border-cat-yellow/30'
                                                    }`}
                                            >
                                                {action.priority}
                                            </span>
                                            <span className="text-xs text-sand/50 italic">{action.owner}</span>
                                        </div>
                                        <h4 className="text-sm font-bold text-white mb-2">
                                            {action.title}
                                        </h4>
                                        <p className="text-xs text-sand/70 mb-3 leading-relaxed">
                                            {action.description}
                                        </p>
                                        <div className="text-xs text-green-400 font-semibold flex items-center gap-1">
                                            <span>📊</span>
                                            Impact: {action.estimated_impact}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Footer */}
                <div className="mt-12 pt-6 border-t border-white/10 text-center">
                    <p className="text-xs text-sand/50">
                        NEEMBA CAT • Concessionnaire officiel Caterpillar • Des machines conçues pour vos défis
                    </p>
                    <p className="text-xs text-sand/40 mt-1">
                        L'excellence Cat au service de vos équipements
                    </p>
                </div>
            </div>

            {/* KPI Detail Modal */}
            {selectedKPI && (
                <KPIDetailModal
                    kpiName={selectedKPI}
                    onClose={() => setSelectedKPI(null)}
                />
            )}
        </div>
    );
};

export default SEPDashboard;
