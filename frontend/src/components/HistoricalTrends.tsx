import { useEffect, useState } from 'react';
import { api } from '../utils/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';

interface Trend {
    metric_name: string;
    current_value: number;
    avg_last_hour: number;
    avg_last_day: number;
    trend_direction: string;
    change_rate: number;
    severity: string;
}

interface Snapshot {
    timestamp: string;
    risk_score: number;
    cpu_usage: Record<string, number> | number;
    memory_usage: Record<string, number> | number;
    error_rates: Record<string, number> | number;
    latencies: Record<string, number> | number;
    bottleneck_count?: number;
    critical_services?: string[];
}

const HistoricalTrends = () => {
    const [trends, setTrends] = useState<Record<string, Trend>>({});
    const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
    const [timeWindow, setTimeWindow] = useState(30);
    const [loading, setLoading] = useState(true);

    // Helper function to calculate average from object or return number
    const getAverage = (value: Record<string, number> | number): number => {
        if (typeof value === 'number') return value;
        const values = Object.values(value || {});
        if (values.length === 0) return 0;
        return values.reduce((a, b) => a + b, 0) / values.length;
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [trendsData, snapshotsData] = await Promise.all([
                    api.getHistoricalTrends(timeWindow),
                    api.getHistoricalSnapshots(timeWindow)
                ]);
                setTrends(trendsData?.trends || {});
                setSnapshots(snapshotsData?.snapshots || []);
                console.log('Historical data loaded:', {
                    trendsCount: Object.keys(trendsData?.trends || {}).length,
                    snapshotsCount: snapshotsData?.snapshots?.length || 0
                });
            } catch (error) {
                console.error('Failed to fetch historical data:', error);
                setTrends({});
                setSnapshots([]);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 15000); // Update every 15s
        return () => clearInterval(interval);
    }, [timeWindow]);

    const getTrendIcon = (direction: string) => {
        switch (direction) {
            case 'increasing': return <TrendingUp className="w-4 h-4 text-red-400" />;
            case 'decreasing': return <TrendingDown className="w-4 h-4 text-green-400" />;
            case 'stable': return <Minus className="w-4 h-4 text-gray-400" />;
            default: return <Activity className="w-4 h-4 text-yellow-400" />;
        }
    };

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical': return 'border-red-500/30 bg-red-500/5';
            case 'warning': return 'border-yellow-500/30 bg-yellow-500/5';
            default: return 'border-green-500/30 bg-green-500/5';
        }
    };

    const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp);
        return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    };

    // Prepare chart data with proper averaging
    const chartData = snapshots.map((snap) => ({
        time: formatTimestamp(snap.timestamp),
        risk: snap.risk_score.toFixed(1),
        cpu: getAverage(snap.cpu_usage).toFixed(1),
        memory: getAverage(snap.memory_usage).toFixed(1),
        errors: getAverage(snap.error_rates).toFixed(1),
        latency: getAverage(snap.latencies).toFixed(0)
    }));

    if (loading) {
        return (
            <div className="glass-panel rounded-2xl p-6">
                <div className="animate-pulse">
                    <div className="h-6 bg-white/10 rounded w-1/4 mb-4"></div>
                    <div className="h-64 bg-white/5 rounded-xl"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="glass-panel rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <Activity className="w-6 h-6 text-purple-400" />
                        <h3 className="text-xl font-bold">Historical Trends</h3>
                    </div>
                    <div className="flex gap-2">
                        {[15, 30, 60].map((min) => (
                            <button
                                key={min}
                                onClick={() => setTimeWindow(min)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${timeWindow === min
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                                    }`}
                            >
                                {min}m
                            </button>
                        ))}
                    </div>
                </div>

                {/* Metric Cards */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                    {Object.entries(trends).map(([key, trend]) => (
                        <div key={key} className={`border rounded-xl p-4 ${getSeverityColor(trend.severity)}`}>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs text-gray-400 uppercase tracking-wider">
                                    {trend.metric_name.replace(/_/g, ' ')}
                                </span>
                                {getTrendIcon(trend.trend_direction)}
                            </div>
                            <div className="text-2xl font-bold mb-1">{trend.current_value.toFixed(1)}</div>
                            <div className="text-xs text-gray-400">
                                Avg: {trend.avg_last_hour.toFixed(1)}
                            </div>
                            <div className={`text-xs mt-1 font-medium ${trend.change_rate > 0 ? 'text-red-400' :
                                trend.change_rate < 0 ? 'text-green-400' :
                                    'text-gray-400'
                                }`}>
                                {trend.change_rate > 0 ? '+' : ''}{trend.change_rate.toFixed(2)}%/min
                            </div>
                        </div>
                    ))}
                </div>

                {/* Chart */}
                <div className="h-80 bg-black/20 rounded-xl p-4">
                    {chartData.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                                <XAxis
                                    dataKey="time"
                                    stroke="#ffffff50"
                                    tick={{ fontSize: 12 }}
                                />
                                <YAxis stroke="#ffffff50" tick={{ fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#12121e',
                                        borderColor: '#333',
                                        borderRadius: '8px'
                                    }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="risk"
                                    stroke="#ef4444"
                                    strokeWidth={2}
                                    dot={false}
                                    name="Risk Score"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="cpu"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    dot={false}
                                    name="CPU %"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="memory"
                                    stroke="#8b5cf6"
                                    strokeWidth={2}
                                    dot={false}
                                    name="Memory %"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="errors"
                                    stroke="#f59e0b"
                                    strokeWidth={2}
                                    dot={false}
                                    name="Error Rate %"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="flex items-center justify-center h-full text-gray-400">
                            <div className="text-center">
                                <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
                                <p>No historical data available yet</p>
                                <p className="text-sm mt-1">Trigger an analysis to start tracking</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default HistoricalTrends;
