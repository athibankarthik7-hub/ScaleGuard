import { useEffect, useState } from 'react';
import { api } from '../utils/api';
import { AlertTriangle, Clock, TrendingDown, Shield, AlertCircle } from 'lucide-react';

interface FailurePrediction {
    service_id: string;
    failure_probability: number;
    estimated_time_minutes: number;
    failure_type: string;
    contributing_factors: string | string[];
    preventive_actions: string | string[];
    severity: string;
}

const PredictionsPanel = () => {
    const [predictions, setPredictions] = useState<FailurePrediction[]>([]);
    const [totalAtRisk, setTotalAtRisk] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPredictions = async () => {
            try {
                const data = await api.getAllPredictions();
                setPredictions(data.failure_predictions || []);
                setTotalAtRisk(data.total_at_risk_services || 0);
            } catch (error) {
                console.error('Failed to fetch predictions:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchPredictions();
        const interval = setInterval(fetchPredictions, 10000); // Update every 10s
        return () => clearInterval(interval);
    }, []);

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical': return 'text-red-500 bg-red-500/10 border-red-500/20';
            case 'high': return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
            case 'medium': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
            default: return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
        }
    };

    const getFailureTypeIcon = (type: string) => {
        switch (type) {
            case 'error_cascade': return AlertTriangle;
            case 'resource_exhaustion': return TrendingDown;
            case 'performance_degradation': return Clock;
            default: return AlertCircle;
        }
    };

    if (loading) {
        return (
            <div className="glass-panel rounded-2xl p-6">
                <div className="animate-pulse">
                    <div className="h-6 bg-white/10 rounded w-1/3 mb-4"></div>
                    <div className="space-y-3">
                        <div className="h-24 bg-white/5 rounded-xl"></div>
                        <div className="h-24 bg-white/5 rounded-xl"></div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="glass-panel rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <Shield className="w-6 h-6 text-blue-400" />
                    <h3 className="text-xl font-bold">Failure Predictions</h3>
                </div>
                <div className="px-3 py-1 rounded-full bg-red-500/20 border border-red-500/30">
                    <span className="text-red-400 text-sm font-medium">{totalAtRisk} At Risk</span>
                </div>
            </div>

            <div className="space-y-4 max-h-[600px] overflow-y-auto">
                {predictions.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                        <Shield className="w-16 h-16 mb-4 text-green-500" />
                        <p className="text-lg font-medium text-green-400">All Systems Healthy</p>
                        <p className="text-sm mt-2">No failure predictions detected</p>
                    </div>
                ) : (
                    predictions.map((pred, i) => {
                        const Icon = getFailureTypeIcon(pred.failure_type);
                        const severityClass = getSeverityColor(pred.severity);

                        return (
                            <div
                                key={i}
                                className={`border rounded-xl p-5 transition-all hover:scale-[1.02] ${severityClass}`}
                            >
                                <div className="flex items-start gap-4">
                                    <div className="mt-1">
                                        <Icon className="w-6 h-6" />
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-start justify-between mb-2">
                                            <div>
                                                <h4 className="font-bold text-lg">{pred.service_id}</h4>
                                                <p className="text-xs text-gray-400 uppercase tracking-wider mt-1">
                                                    {pred.failure_type.replace(/_/g, ' ')}
                                                </p>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-2xl font-bold">{pred.failure_probability.toFixed(2)}%</div>
                                                <div className="text-xs text-gray-400 mt-1">
                                                    <Clock className="w-3 h-3 inline mr-1" />
                                                    {pred.estimated_time_minutes < 60
                                                        ? `in ${pred.estimated_time_minutes}m`
                                                        : pred.estimated_time_minutes < 1440
                                                            ? `in ${Math.floor(pred.estimated_time_minutes / 60)}h ${pred.estimated_time_minutes % 60}m`
                                                            : `in ${Math.floor(pred.estimated_time_minutes / 1440)}d ${Math.floor((pred.estimated_time_minutes % 1440) / 60)}h`
                                                    }
                                                </div>
                                            </div>
                                        </div>

                                        <div className="mt-3 p-3 rounded-lg bg-black/20">
                                            <p className="text-sm font-medium mb-2">Contributing Factors:</p>
                                            {Array.isArray(pred.contributing_factors) ? (
                                                <ul className="text-xs text-gray-300 leading-relaxed space-y-1">
                                                    {pred.contributing_factors.map((factor, idx) => (
                                                        <li key={idx} className="flex gap-2">
                                                            <span className="text-red-400">•</span>
                                                            <span>{factor}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            ) : (
                                                <p className="text-xs text-gray-300 leading-relaxed">{pred.contributing_factors}</p>
                                            )}
                                        </div>

                                        <div className="mt-3 p-3 rounded-lg bg-black/20 border border-white/5">
                                            <p className="text-sm font-medium mb-2 text-blue-400">Preventive Actions:</p>
                                            {Array.isArray(pred.preventive_actions) ? (
                                                <ul className="text-xs text-gray-300 leading-relaxed space-y-1">
                                                    {pred.preventive_actions.map((action, idx) => (
                                                        <li key={idx} className="flex gap-2">
                                                            <span className="text-blue-400">→</span>
                                                            <span>{action}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            ) : (
                                                <p className="text-xs text-gray-300 leading-relaxed">{pred.preventive_actions}</p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
};

export default PredictionsPanel;
