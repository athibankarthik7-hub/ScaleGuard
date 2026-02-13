import { useState, useEffect } from 'react';
import { Clock, AlertOctagon, Search, Brain, TrendingUp } from 'lucide-react';
import { api } from '../utils/api';

interface RootCauseAnalysis {
    primary_bottlenecks: Array<{
        id: string;
        name: string;
        type: string;
        risk_score: number;
        centrality: number;
        cpu_usage: number;
        memory_usage: number;
        reason: string;
    }>;
    cascading_failures: string[];
    recommended_actions: string[];
    risk_score: number;
    ai_insights: string | null;
}

const IncidentDebugger = () => {
    const [selectedIncident, setSelectedIncident] = useState<number | null>(null);
    const [analysis, setAnalysis] = useState<RootCauseAnalysis | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchAnalysis = async () => {
            setLoading(true);
            try {
                const data = await api.getAnalysis();
                setAnalysis(data);
            } catch (e) {
                console.error("Failed to fetch analysis", e);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalysis();
        const interval = setInterval(fetchAnalysis, 10000);
        return () => clearInterval(interval);
    }, []);

    const incidents = analysis?.primary_bottlenecks?.slice(0, 5).map((b, idx) => ({
        id: idx + 1,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        service: b.name,
        error: b.reason,
        severity: b.risk_score > 75 ? 'critical' : b.risk_score > 50 ? 'high' : 'warning',
        details: b
    })) || [];

    return (
        <div className="p-6 lg:p-10 text-white w-full max-w-7xl mx-auto h-full flex flex-col">
            <header className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Incident Debugger</h1>
                <p className="text-gray-400">Trace failures, analyze logs, and pinpoint root causes with AI insights.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
                <div className="glass-panel p-0 rounded-2xl overflow-hidden flex flex-col">
                    <div className="p-4 border-b border-white/10 bg-white/5">
                        <h3 className="font-semibold flex items-center gap-2">
                            <Clock size={16} /> Active Bottlenecks
                        </h3>
                    </div>
                    <div className="overflow-y-auto flex-1 p-2 space-y-2">
                        {loading ? (
                            <div className="text-center text-gray-400 py-8">Loading...</div>
                        ) : incidents.length === 0 ? (
                            <div className="text-center text-gray-400 py-8">No bottlenecks detected</div>
                        ) : (
                            incidents.map((inc) => (
                                <div
                                    key={inc.id}
                                    onClick={() => setSelectedIncident(inc.id)}
                                    className={`p-4 rounded-xl cursor-pointer transition-colors border border-transparent ${selectedIncident === inc.id ? 'bg-primary/20 border-primary/50' : 'hover:bg-white/5 hover:border-white/10'}`}
                                >
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="font-bold text-sm text-gray-200">{inc.service}</span>
                                        <span className="text-xs text-gray-500">{inc.time}</span>
                                    </div>
                                    <div className={`text-xs font-medium px-2 py-1 rounded inline-block mb-2 ${inc.severity === 'critical' ? 'bg-red-500/20 text-red-400' : inc.severity === 'high' ? 'bg-orange-500/20 text-orange-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                                        {inc.error}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col max-h-[700px] overflow-y-auto">
                    {selectedIncident && analysis ? (
                        <>
                            <div className="flex justify-between items-start mb-6 pb-6 border-b border-white/10 flex-shrink-0">
                                <div>
                                    <h2 className="text-2xl font-bold flex items-center gap-3">
                                        <AlertOctagon className="text-red-500" />
                                        Bottleneck Analysis #{selectedIncident}
                                    </h2>
                                    <p className="text-gray-400 mt-1">AI-powered root cause detection</p>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm text-gray-400">Risk Score</div>
                                    <div className="text-2xl font-bold text-red-400">{analysis.risk_score.toFixed(1)}</div>
                                </div>
                            </div>

                            {analysis.ai_insights && (
                                <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 p-5 rounded-xl border border-purple-500/30 mb-6 shadow-lg flex-shrink-0">
                                    <div className="flex items-center gap-3 mb-3">
                                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center shadow-lg">
                                            <Brain size={20} className="text-white" />
                                        </div>
                                        <h4 className="font-bold text-purple-200 text-base">AI-Powered Root Cause Analysis</h4>
                                    </div>
                                    <div className="text-sm text-gray-200 whitespace-pre-wrap break-words leading-relaxed pl-13 max-h-64 overflow-y-auto">{analysis.ai_insights}</div>
                                </div>
                            )}

                            <div className="grid grid-cols-2 gap-4 mb-6 flex-shrink-0">
                                <div className="bg-gradient-to-br from-red-900/20 to-orange-900/20 p-5 rounded-xl border border-red-500/20 shadow-md">
                                    <h4 className="text-xs text-red-300 uppercase mb-3 font-bold tracking-wider flex items-center gap-2">
                                        <TrendingUp size={14} />
                                        Primary Bottlenecks
                                    </h4>
                                    <div className="space-y-3">
                                        {analysis.primary_bottlenecks.slice(0, 3).map((b, idx) => (
                                            <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-black/30 border border-red-500/20 hover:border-red-500/40 transition-colors">
                                                <span className="w-2 h-2 mt-2 rounded-full bg-red-500 flex-shrink-0 animate-pulse shadow-lg shadow-red-500/50" />
                                                <div className="flex-1">
                                                    <div className="text-red-300 font-bold text-sm mb-1">{b.name}</div>
                                                    <div className="text-xs text-gray-400 flex gap-3">
                                                        <span>CPU: <span className="text-red-400 font-semibold">{b.cpu_usage.toFixed(0)}%</span></span>
                                                        <span>Mem: <span className="text-orange-400 font-semibold">{b.memory_usage.toFixed(0)}%</span></span>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className="bg-gradient-to-br from-orange-900/20 to-yellow-900/20 p-5 rounded-xl border border-orange-500/20 shadow-md">
                                    <h4 className="text-xs text-orange-300 uppercase mb-3 font-bold tracking-wider">Blast Radius</h4>
                                    <div className="text-orange-400 font-bold text-3xl mb-2">
                                        {analysis.cascading_failures.length}
                                    </div>
                                    <div className="text-sm text-orange-200 mb-3">Service{analysis.cascading_failures.length !== 1 ? 's' : ''} at Risk</div>
                                    <div className="text-xs text-gray-400 space-y-1 max-h-24 overflow-y-auto">
                                        {analysis.cascading_failures.slice(0, 4).map((failure, idx) => (
                                            <div key={idx} className="flex items-start gap-2">
                                                <span className="text-orange-500">•</span>
                                                <span className="flex-1">{failure}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className="bg-gradient-to-br from-green-900/20 to-emerald-900/20 rounded-xl p-5 mb-4 border border-green-500/20 flex-shrink-0">
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center">
                                        <span className="text-green-400 text-lg font-bold">✓</span>
                                    </div>
                                    <h4 className="text-sm font-bold text-green-300 uppercase tracking-wide">AI-Powered Recommendations</h4>
                                </div>
                                <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
                                    {analysis.recommended_actions.map((action, idx) => (
                                        <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-black/20 border border-green-500/10 hover:border-green-500/30 transition-colors group">
                                            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center text-green-400 font-bold text-xs mt-0.5 group-hover:bg-green-500/30 transition-colors">
                                                {idx + 1}
                                            </div>
                                            <span className="text-gray-200 text-sm leading-relaxed break-words">{action}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="flex-shrink-0 bg-black/40 rounded-xl p-4 font-mono text-xs text-gray-300 overflow-auto border border-white/5 max-h-48">
                                <div className="mb-2 text-gray-500 border-b border-gray-800 pb-2">
                                    <span className="font-bold">System Metrics</span>
                                </div>
                                <div className="space-y-2">
                                    {incidents.find(i => i.id === selectedIncident)?.details && (
                                        <>
                                            <div><span className="text-blue-400">Service Type:</span> {incidents.find(i => i.id === selectedIncident)?.details.type}</div>
                                            <div><span className="text-blue-400">Risk Score:</span> {incidents.find(i => i.id === selectedIncident)?.details.risk_score.toFixed(2)}</div>
                                            <div><span className="text-blue-400">Centrality:</span> {incidents.find(i => i.id === selectedIncident)?.details.centrality.toFixed(4)}</div>
                                            <div><span className="text-blue-400">CPU Usage:</span> {incidents.find(i => i.id === selectedIncident)?.details.cpu_usage.toFixed(1)}%</div>
                                            <div><span className="text-blue-400">Memory Usage:</span> {incidents.find(i => i.id === selectedIncident)?.details.memory_usage.toFixed(1)}%</div>
                                        </>
                                    )}
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
                            <Search size={48} className="mb-4 opacity-50" />
                            <p>Select a bottleneck to investigate root cause.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default IncidentDebugger;
