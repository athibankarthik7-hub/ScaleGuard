import { useEffect, useState, cloneElement } from 'react';
import { api } from '../utils/api';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertTriangle, CheckCircle, Activity, Server, Database, Zap, Brain, TrendingUp, Wrench } from 'lucide-react';
import PredictionsPanel from '../components/PredictionsPanel';
import HistoricalTrends from '../components/HistoricalTrends';
import RemediationPanel from '../components/RemediationPanel';

interface Bottleneck {
    id: string;
    name: string;
    type: string;
    risk_score: number;
    centrality: number;
    cpu_usage: number;
    memory_usage: number;
    reason: string;
}

const Dashboard = () => {
    const [riskScore, setRiskScore] = useState<number | null>(null);
    const [system, setSystem] = useState<any>(null);
    const [bottlenecks, setBottlenecks] = useState<Bottleneck[]>([]);
    const [activeTab, setActiveTab] = useState<'overview' | 'trends' | 'predictions' | 'remediation'>('overview');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [rs, sys, bn] = await Promise.all([
                    api.getRiskScore(),
                    api.getSystem(),
                    api.getBottlenecks()
                ]);
                setRiskScore(rs.risk_score);
                setSystem(sys);
                setBottlenecks(bn.bottlenecks || []);
            } catch (e) {
                console.error("Failed to fetch dashboard data", e);
            }
        };
        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    // Mock chart data
    const data = [
        { name: '00:00', traffic: 4000, risk: 24 },
        { name: '04:00', traffic: 3000, risk: 13 },
        { name: '08:00', traffic: 2000, risk: 18 },
        { name: '12:00', traffic: 2780, risk: 39 },
        { name: '16:00', traffic: 1890, risk: 48 },
        { name: '20:00', traffic: 2390, risk: 38 },
        { name: '24:00', traffic: 3490, risk: 43 },
    ];

    return (
        <div className="p-6 lg:p-10 text-white w-full max-w-7xl mx-auto">
            <header className="mb-8">
                <h1 className="text-3xl font-bold mb-2">System Overview</h1>
                <p className="text-gray-400">Real-time health monitoring and predictive risk analysis powered by JARVIS AI.</p>
            </header>

            {/* Enhanced Tab Navigation */}
            <div className="flex gap-2 mb-8 overflow-x-auto">
                <button
                    onClick={() => setActiveTab('overview')}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all whitespace-nowrap ${activeTab === 'overview'
                            ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30'
                            : 'bg-white/5 text-gray-400 hover:bg-white/10'
                        }`}
                >
                    <Activity className="w-5 h-5" />
                    Overview
                </button>
                <button
                    onClick={() => setActiveTab('trends')}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all whitespace-nowrap ${activeTab === 'trends'
                            ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/30'
                            : 'bg-white/5 text-gray-400 hover:bg-white/10'
                        }`}
                >
                    <TrendingUp className="w-5 h-5" />
                    Historical Trends
                </button>
                <button
                    onClick={() => setActiveTab('predictions')}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all whitespace-nowrap ${activeTab === 'predictions'
                            ? 'bg-red-500 text-white shadow-lg shadow-red-500/30'
                            : 'bg-white/5 text-gray-400 hover:bg-white/10'
                        }`}
                >
                    <Brain className="w-5 h-5" />
                    AI Predictions
                </button>
                <button
                    onClick={() => setActiveTab('remediation')}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all whitespace-nowrap ${activeTab === 'remediation'
                            ? 'bg-green-500 text-white shadow-lg shadow-green-500/30'
                            : 'bg-white/5 text-gray-400 hover:bg-white/10'
                        }`}
                >
                    <Wrench className="w-5 h-5" />
                    Auto-Remediation
                </button>
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <StatCard
                            label="Scaling Risk Score"
                            value={riskScore ? riskScore.toFixed(0) : '--'}
                            unit="/ 100"
                            trend={riskScore && riskScore > 50 ? 'High' : 'Low'}
                            trendColor={riskScore && riskScore > 50 ? 'text-red-500' : 'text-green-500'}
                            icon={<AlertTriangle />}
                        />
                        <StatCard
                            label="Active Services"
                            value={system?.nodes?.length || '--'}
                            unit="Nodes"
                            icon={<Server />}
                        />
                        <StatCard
                            label="Total Traffic"
                            value="24.5k"
                            unit="RPM"
                            trend="+12%"
                            trendColor="text-green-500"
                            icon={<Activity />}
                        />
                        <StatCard
                            label="System Health"
                            value="98.2%"
                            unit="Uptime"
                            icon={<CheckCircle />}
                        />
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2 glass-panel rounded-2xl p-6 h-[400px]">
                            <h3 className="text-lg font-semibold mb-6">Traffic vs Risk Correlation</h3>
                            <ResponsiveContainer width="100%" height="85%">
                                <AreaChart data={data}>
                                    <defs>
                                        <linearGradient id="colorTraffic" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                                    <XAxis dataKey="name" stroke="#ffffff50" />
                                    <YAxis stroke="#ffffff50" />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#12121e', borderColor: '#333' }}
                                        itemStyle={{ color: '#fff' }}
                                    />
                                    <Area type="monotone" dataKey="traffic" stroke="#3b82f6" fillOpacity={1} fill="url(#colorTraffic)" />
                                    <Area type="monotone" dataKey="risk" stroke="#ef4444" fillOpacity={1} fill="url(#colorRisk)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="glass-panel rounded-2xl p-6 h-[400px] overflow-y-auto">
                            <h3 className="text-lg font-semibold mb-4">Active Bottlenecks</h3>
                            <div className="space-y-4">
                                {bottlenecks.length === 0 ? (
                                    <div className="flex items-center justify-center h-32 text-gray-400">
                                        <div className="text-center">
                                            <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
                                            <p className="text-sm">No bottlenecks detected</p>
                                        </div>
                                    </div>
                                ) : (
                                    bottlenecks.slice(0, 5).map((bn, i) => {
                                        const getSeverityIcon = (risk: number) => {
                                            if (risk > 75) return { icon: AlertTriangle, color: 'text-red-500' };
                                            if (risk > 50) return { icon: Zap, color: 'text-orange-500' };
                                            return { icon: Activity, color: 'text-yellow-500' };
                                        };
                                        const { icon: Icon, color } = getSeverityIcon(bn.risk_score);

                                        return (
                                            <div key={i} className="flex gap-4 p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
                                                <div className="mt-1">
                                                    <Icon className={`w-5 h-5 ${color}`} />
                                                </div>
                                                <div className="flex-1">
                                                    <div className="flex justify-between items-start mb-1">
                                                        <h4 className="font-medium text-sm">{bn.name}</h4>
                                                        <span className="text-xs text-gray-500">{bn.type}</span>
                                                    </div>
                                                    <p className="text-xs text-gray-400 mt-1">{bn.reason}</p>
                                                    <div className="flex gap-3 mt-2 text-[10px] text-gray-500">
                                                        <span>Risk: {bn.risk_score.toFixed(0)}</span>
                                                        <span>CPU: {bn.cpu_usage.toFixed(0)}%</span>
                                                        <span>Mem: {bn.memory_usage.toFixed(0)}%</span>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })
                                )}
                            </div>
                        </div>
                    </div>
                </>
            )}

            {activeTab === 'trends' && <HistoricalTrends />}
            {activeTab === 'predictions' && <PredictionsPanel />}
            {activeTab === 'remediation' && <RemediationPanel />}
        </div>
    );
};

const StatCard = ({ label, value, unit, trend, trendColor, icon }: any) => (
    <div className="glass-panel p-6 rounded-2xl relative overflow-hidden group">
        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
            {cloneElement(icon, { size: 48 })}
        </div>
        <div className="relative z-10">
            <div className="flex items-center gap-2 mb-2 text-gray-400 text-sm font-medium">
                {icon} {label}
            </div>
            <div className="flex items-end gap-2">
                <span className="text-3xl font-bold tracking-tight">{value}</span>
                <span className="text-sm text-gray-500 mb-1">{unit}</span>
            </div>
            {trend && (
                <div className={`text-xs mt-2 ${trendColor} font-medium`}>
                    {trend} vs last hour
                </div>
            )}
        </div>
    </div>
);

export default Dashboard;
