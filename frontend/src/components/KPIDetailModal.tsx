import React, { useState, useEffect } from 'react';
import { X, TrendingUp, AlertCircle, CheckCircle, Lightbulb, Target, Calendar } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface KPIDetailModalProps {
    kpiName: string;
    onClose: () => void;
}

interface KPIDetail {
    kpi_name: string;
    current_value: number;
    target: number;
    unit: string;
    trend: { month: string; value: number }[];
    insights: {
        type: string;
        priority: string;
        message: string;
        details: string;
    }[];
    actions: {
        id: string;
        title: string;
        description: string;
        priority: string;
        owner: string;
        estimated_impact: string;
        timeline: string;
        status: string;
    }[];
    forecast: { month: string; predicted: number; confidence: number }[];
}

function KPIDetailModal({ kpiName, onClose }: KPIDetailModalProps) {
    const [detail, setDetail] = useState<KPIDetail | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDetail = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/sep/kpi/${encodeURIComponent(kpiName)}/details`);
                const data = await response.json();
                setDetail(data);
            } catch (error) {
                console.error('Error fetching KPI details:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchDetail();
    }, [kpiName]);

    if (loading) {
        return (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
                <div className="bg-onyx border-2 border-cat-yellow rounded-2xl p-8">
                    <div className="text-cat-yellow text-xl">Chargement...</div>
                </div>
            </div>
        );
    }

    if (!detail) {
        return null;
    }

    // Combine trend and forecast for the chart
    const chartData = [
        ...detail.trend,
        ...detail.forecast.map(f => ({
            month: f.month,
            value: f.predicted,
            isForecast: true
        }))
    ];

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto">
            <div className="bg-gradient-to-br from-onyx via-black to-onyx border-2 border-cat-yellow/30 rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">

                {/* Header */}
                <div className="sticky top-0 bg-onyx border-b-2 border-cat-yellow/20 p-6 flex items-center justify-between">
                    <div>
                        <h2 className="text-3xl font-black text-white mb-2">{detail.kpi_name}</h2>
                        <div className="flex items-center gap-4">
                            <div className="text-cat-yellow text-2xl font-bold">{detail.current_value}{detail.unit}</div>
                            <div className="text-sand/60">Objectif: {detail.target}{detail.unit}</div>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="h-10 w-10 rounded-full bg-cat-yellow/10 hover:bg-cat-yellow/20 flex items-center justify-center transition-all"
                    >
                        <X size={24} className="text-cat-yellow" />
                    </button>
                </div>

                <div className="p-6 space-y-6">

                    {/* Trend Chart */}
                    <div className="bg-black/60 backdrop-blur-sm border-2 border-white/10 rounded-xl p-6">
                        <div className="flex items-center gap-2 mb-4">
                            <TrendingUp className="text-cat-yellow" size={24} />
                            <h3 className="text-xl font-bold text-white">Évolution sur 12 mois + Prévisions</h3>
                        </div>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                                <XAxis
                                    dataKey="month"
                                    stroke="#F2E8DA"
                                    tick={{ fill: '#F2E8DA', fontSize: 12 }}
                                />
                                <YAxis
                                    stroke="#F2E8DA"
                                    tick={{ fill: '#F2E8DA', fontSize: 12 }}
                                    domain={['dataMin - 5', 'dataMax + 5']}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#000',
                                        border: '2px solid #FFCD11',
                                        borderRadius: '8px',
                                        color: '#F2E8DA'
                                    }}
                                />
                                <ReferenceLine
                                    y={detail.target}
                                    stroke="#FFCD11"
                                    strokeDasharray="5 5"
                                    label={{ value: 'Objectif', fill: '#FFCD11', position: 'right' }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="value"
                                    stroke="#FFCD11"
                                    strokeWidth={3}
                                    dot={{ fill: '#FFCD11', r: 4 }}
                                    activeDot={{ r: 6 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* AI Insights */}
                    <div className="bg-black/60 backdrop-blur-sm border-2 border-white/10 rounded-xl p-6">
                        <div className="flex items-center gap-2 mb-4">
                            <Lightbulb className="text-cat-yellow" size={24} />
                            <h3 className="text-xl font-bold text-white">Insights IA</h3>
                        </div>
                        <div className="space-y-3">
                            {detail.insights.map((insight, idx) => (
                                <div
                                    key={idx}
                                    className="bg-black/60 border-l-4 rounded-lg p-4"
                                    style={{
                                        borderLeftColor: insight.type === 'warning' ? '#ef4444' : insight.type === 'success' ? '#10b981' : '#3b82f6'
                                    }}
                                >
                                    <div className="flex items-start gap-3">
                                        {insight.type === 'warning' && <AlertCircle className="text-red-400 mt-1" size={20} />}
                                        {insight.type === 'success' && <CheckCircle className="text-green-400 mt-1" size={20} />}
                                        {insight.type === 'info' && <Lightbulb className="text-blue-400 mt-1" size={20} />}
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <div className="text-white font-semibold">{insight.message}</div>
                                                <span className={`text-xs px-2 py-1 rounded ${insight.priority === 'HIGH' ? 'bg-red-500/20 text-red-300' : 'bg-yellow-500/20 text-yellow-300'
                                                    }`}>
                                                    {insight.priority}
                                                </span>
                                            </div>
                                            <div className="text-sand/70 text-sm">{insight.details}</div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Corrective Actions */}
                    <div className="bg-black/60 backdrop-blur-sm border-2 border-white/10 rounded-xl p-6">
                        <div className="flex items-center gap-2 mb-4">
                            <Target className="text-cat-yellow" size={24} />
                            <h3 className="text-xl font-bold text-white">Actions Correctives Suggérées</h3>
                        </div>
                        <div className="space-y-4">
                            {detail.actions.map((action) => (
                                <div
                                    key={action.id}
                                    className="bg-black/60 border-2 border-white/10 rounded-xl p-4 hover:border-cat-yellow/50 transition-all"
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <h4 className="text-white font-bold text-lg">{action.title}</h4>
                                                <span className={`text-xs px-2 py-1 rounded ${action.priority === 'HIGH' ? 'bg-red-500/20 text-red-300' : 'bg-yellow-500/20 text-yellow-300'
                                                    }`}>
                                                    {action.priority}
                                                </span>
                                            </div>
                                            <p className="text-sand/70 text-sm mb-3">{action.description}</p>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-3 gap-4 text-sm">
                                        <div>
                                            <div className="text-sand/60 text-xs mb-1">Responsable</div>
                                            <div className="text-white">{action.owner}</div>
                                        </div>
                                        <div>
                                            <div className="text-sand/60 text-xs mb-1">Impact Estimé</div>
                                            <div className="text-cat-yellow font-semibold">{action.estimated_impact}</div>
                                        </div>
                                        <div>
                                            <div className="text-sand/60 text-xs mb-1 flex items-center gap-1">
                                                <Calendar size={12} />
                                                Timeline
                                            </div>
                                            <div className="text-white">{action.timeline}</div>
                                        </div>
                                    </div>
                                    <button className="mt-4 w-full bg-cat-yellow text-onyx font-bold py-2 px-4 rounded-lg hover:bg-cat-yellow/90 transition-all">
                                        Mettre en œuvre cette action
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
}

export default KPIDetailModal;
