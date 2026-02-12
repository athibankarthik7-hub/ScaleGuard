import { useState } from 'react';
import { Clock, AlertOctagon, Search } from 'lucide-react';

const IncidentDebugger = () => {
    const [selectedIncident, setSelectedIncident] = useState<number | null>(null);

    const incidents = [
        { id: 1, time: '10:42 AM', service: 'Payment Service', error: 'Connection Timeout', severity: 'critical' },
        { id: 2, time: '10:45 AM', service: 'Order Service', error: '503 Service Unavailable', severity: 'high' },
        { id: 3, time: '11:00 AM', service: 'User Service', error: 'High Latency (>2s)', severity: 'warning' },
    ];

    return (
        <div className="p-6 lg:p-10 text-white w-full max-w-7xl mx-auto h-full flex flex-col">
            <header className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Incident Debugger</h1>
                <p className="text-gray-400">Trace failures, analyze logs, and pinpoint root causes.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
                <div className="glass-panel p-0 rounded-2xl overflow-hidden flex flex-col">
                    <div className="p-4 border-b border-white/10 bg-white/5">
                        <h3 className="font-semibold flex items-center gap-2">
                            <Clock size={16} /> Recent Incidents
                        </h3>
                    </div>
                    <div className="overflow-y-auto flex-1 p-2 space-y-2">
                        {incidents.map((inc) => (
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
                        ))}
                    </div>
                </div>

                <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col">
                    {selectedIncident ? (
                        <>
                            <div className="flex justify-between items-start mb-6 pb-6 border-b border-white/10">
                                <div>
                                    <h2 className="text-2xl font-bold flex items-center gap-3">
                                        <AlertOctagon className="text-red-500" />
                                        Incident #{selectedIncident}
                                    </h2>
                                    <p className="text-gray-400 mt-1">Root Cause Analysis in progress...</p>
                                </div>
                                <button className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 text-sm font-medium">
                                    Export Report
                                </button>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="bg-black/20 p-4 rounded-xl border border-white/5">
                                    <h4 className="text-xs text-gray-500 uppercase mb-2">Likely Root Cause</h4>
                                    <div className="flex items-center gap-2 text-red-400 font-bold">
                                        <span className="w-2 h-2 rounded-full bg-red-500" />
                                        Database Connection Pool Exhausted
                                    </div>
                                    <p className="text-xs text-gray-400 mt-2">
                                        Payment DB connection limit reached at 10:41:55 AM.
                                    </p>
                                </div>
                                <div className="bg-black/20 p-4 rounded-xl border border-white/5">
                                    <h4 className="text-xs text-gray-500 uppercase mb-2">Blast Radius</h4>
                                    <div className="text-orange-400 font-bold">
                                        3 Downstream Services
                                    </div>
                                    <p className="text-xs text-gray-400 mt-2">
                                        Order Service, Notification Service, Frontend API
                                    </p>
                                </div>
                            </div>

                            <div className="flex-1 bg-black/40 rounded-xl p-4 font-mono text-xs text-gray-300 overflow-auto border border-white/5">
                                <div className="mb-2 text-gray-500 border-b border-gray-800 pb-2 flex gap-4">
                                    <span>TIMESTAMP</span>
                                    <span>LEVEL</span>
                                    <span>MESSAGE</span>
                                </div>
                                <div className="space-y-1">
                                    <div className="flex gap-4"><span className="text-gray-500">10:41:55.102</span><span className="text-red-500">ERROR</span><span>[PaymentDB] FATAL: remaining connection slots are reserved for non-replication superuser connections</span></div>
                                    <div className="flex gap-4"><span className="text-gray-500">10:41:55.105</span><span className="text-red-500">ERROR</span><span>[PaymentService] ConnectionRefusedError: FATAL: remaining connection slots are reserved</span></div>
                                    <div className="flex gap-4"><span className="text-gray-500">10:41:55.200</span><span className="text-orange-500">WARN</span><span>[OrderService] Retrying payment request (attempt 1/3)...</span></div>
                                    <div className="flex gap-4"><span className="text-gray-500">10:41:56.200</span><span className="text-orange-500">WARN</span><span>[OrderService] Retrying payment request (attempt 2/3)...</span></div>
                                    <div className="flex gap-4"><span className="text-gray-500">10:41:57.200</span><span className="text-red-500">ERROR</span><span>[OrderService] Circuit breaker open for PaymentService</span></div>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
                            <Search size={48} className="mb-4 opacity-50" />
                            <p>Select an incident to investigate root cause.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default IncidentDebugger;
