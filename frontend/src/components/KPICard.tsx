import React from 'react';

interface KPICardProps {
    name: string;
    value: number;
    target_excellent: number;
    target_advanced: number;
    target_emerging: number;
    unit: string;
    performance: 'EXCELLENT' | 'ADVANCED' | 'EMERGING' | 'BASIC';
    weight: number;
    time_period: string;
    data_source: string;
    mode: 'calculated' | 'manual';
    description: string;
    onClick?: () => void;
}

const KPICard: React.FC<KPICardProps> = ({
    name,
    value,
    target_excellent,
    target_advanced,
    target_emerging,
    unit,
    performance,
    weight,
    time_period,
    data_source,
    mode,
    description,
    onClick
}) => {
    const getPerformanceColor = () => {
        switch (performance) {
            case 'EXCELLENT':
                return 'bg-green-500/20 border-green-500 text-green-300';
            case 'ADVANCED':
                return 'bg-cat-yellow/20 border-cat-yellow text-cat-yellow';
            case 'EMERGING':
                return 'bg-orange-500/20 border-orange-500 text-orange-300';
            default:
                return 'bg-red-500/20 border-red-500 text-red-300';
        }
    };

    const getPerformanceIcon = () => {
        switch (performance) {
            case 'EXCELLENT':
                return '🏆';
            case 'ADVANCED':
                return '🟡';
            case 'EMERGING':
                return '🟠';
            default:
                return '🔴';
        }
    };

    const getModeIcon = () => {
        return mode === 'calculated' ? '🧮' : '📝';
    };

    return (
        <div
            className={`bg-onyx/80 border-2 border-white/10 rounded-xl p-4 hover:border-cat-yellow/50 transition-all duration-300 ${onClick ? 'cursor-pointer hover:scale-105' : ''}`}
            onClick={onClick}
        >
            {/* Header */}
            <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                    <h3 className="text-sm font-bold text-white mb-1">{name}</h3>
                    <p className="text-xs text-sand/60">{description}</p>
                </div>
                <span className="text-lg ml-2">{getModeIcon()}</span>
            </div>

            {/* Value */}
            <div className="mb-3">
                <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold text-cat-yellow">
                        {value}
                    </span>
                    <span className="text-lg text-sand/70">{unit}</span>
                </div>
            </div>

            {/* Performance Badge */}
            <div className="mb-3">
                <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold border-2 ${getPerformanceColor()}`}>
                    <span>{getPerformanceIcon()}</span>
                    <span>{performance}</span>
                </span>
            </div>

            {/* Targets */}
            <div className="space-y-1 mb-3 text-xs">
                <div className="flex justify-between text-sand/60">
                    <span>🏆 Excellent:</span>
                    <span className="font-mono">{target_excellent}{unit}</span>
                </div>
                <div className="flex justify-between text-sand/60">
                    <span>🟡 Advanced:</span>
                    <span className="font-mono">{target_advanced}{unit}</span>
                </div>
                <div className="flex justify-between text-sand/60">
                    <span>🟠 Emerging:</span>
                    <span className="font-mono">{target_emerging}{unit}</span>
                </div>
            </div>

            {/* Footer */}
            <div className="pt-3 border-t border-white/10 flex justify-between items-center text-xs text-sand/50">
                <span>{time_period}</span>
                <span>Weight: {weight}%</span>
            </div>
        </div>
    );
};

export default KPICard;
