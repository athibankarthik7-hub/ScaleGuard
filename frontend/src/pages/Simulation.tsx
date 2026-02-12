import { useState } from 'react';
import { api } from '../utils/api';
import { Play, RotateCcw, Zap, Activity } from 'lucide-react';
import { Tooltip, ResponsiveContainer, BarChart, Bar, CartesianGrid, XAxis, YAxis, Legend } from 'recharts';

const Simulation = () => {
    const [growthFactor, setGrowthFactor] = useState(1.5);
    const [duration, setDuration] = useState(60);
    const [results, setResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const runSimulation = async () => {
        setLoading(true);
        try {
            const data = await api.simulate({
                traffic_growth_factor: growthFactor,
                duration_seconds: duration
            });
            setResults(data);
        } catch (e) {
            console.error("Simulation failed", e);
        } finally {
            setLoading(false);
        }
    };

    const resetSystem = async () => {
        await api.reset();
        setResults(null);
    };

    return (
        <div className="p-6 lg:p-10 text-white w-full max-w-7xl mx-auto h-full flex flex-col">
            <header className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Scaling Simulation Lab</h1>
                <p className="text-gray-400">Stress test your architecture with predictive traffic modeling.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1">
                {/* Controls */}
                <div className="glass-panel p-6 rounded-2xl h-fit">
                    <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                        <Zap className="text-yellow-400" /> Configuration
                    </h3>

                    <div className="space-y-6">
                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Traffic Growth Factor (x)</label>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                step="0.5"
                                value={growthFactor}
                                onChange={(e) => setGrowthFactor(parseFloat(e.target.value))}
                                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                            />
                            <div className="mt-2 text-right font-mono text-primary text-lg">{growthFactor}x</div>
                        </div>

                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Duration (Seconds)</label>
                            <input
                                type="number"
                                value={duration}
                                onChange={(e) => setDuration(parseInt(e.target.value))}
                                className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-primary"
                            />
                        </div>

                        <div className="pt-4 flex gap-4">
                            <button
                                onClick={runSimulation}
                                disabled={loading}
                                className={`flex-1 py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${loading ? 'bg-gray-600 cursor-not-allowed' : 'bg-primary hover:bg-blue-600 shadow-lg shadow-primary/20'}`}
                            >
                                {loading ? 'Simulating...' : <><Play size={18} /> Run Simulation</>}
                            </button>
                            <button
                                onClick={resetSystem}
                                className="px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-colors"
                            >
                                <RotateCcw size={18} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Results Visualization */}
                <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col">
                    <h3 className="text-xl font-semibold mb-6">Simulation Results</h3>

                    {results ? (
                        <div className="space-y-8 flex-1">
                            <div className="grid grid-cols-3 gap-4">
                                <ResultStat label="Impacted Services" value={results.nodes.filter((n: any) => n.status !== 'healthy').length} color="text-red-400" />
                                <ResultStat label="Peak Latency" value="1.2s" color="text-yellow-400" />
                                <ResultStat label="Success Rate" value="94.5%" color="text-green-400" />
                            </div>

                            <div className="h-64 w-full">
                                <h4 className="text-sm text-gray-400 mb-4">Resource Usage by Service</h4>
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={results.nodes.slice(0, 10)}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                                        <XAxis dataKey="name" stroke="#ffffff50" fontSize={10} angle={-15} textAnchor="end" />
                                        <YAxis stroke="#ffffff50" />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#12121e', borderColor: '#333' }}
                                            cursor={{ fill: '#ffffff10' }}
                                        />
                                        <Legend />
                                        <Bar dataKey="cpu_usage" name="CPU %" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                                        <Bar dataKey="memory_usage" name="Mem %" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-gray-500 border-2 border-dashed border-white/5 rounded-xl">
                            <Activity size={48} className="mb-4 opacity-50" />
                            <p>Configure and run a simulation to see impact analysis.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

const ResultStat = ({ label, value, color }: any) => (
    <div className="bg-white/5 rounded-xl p-4 text-center">
        <div className={`text-2xl font-bold ${color} mb-1`}>{value}</div>
        <div className="text-xs text-gray-400 uppercase tracking-wider">{label}</div>
    </div>
);

export default Simulation;
