import { useState, useEffect } from 'react';
import ReactFlow, { Background, Controls, MiniMap, useNodesState, useEdgesState } from 'reactflow';
import 'reactflow/dist/style.css';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
import { api } from '../utils/api';
import { Layers, Box, Plus, Upload, Trash2, RefreshCw } from 'lucide-react';

const ArchitectureHelper = () => {
    const [viewMode, setViewMode] = useState<'2d' | '3d'>('2d');
    const [showInputPanel, setShowInputPanel] = useState(false);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [systemData, setSystemData] = useState<any>(null);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
    const [loading, setLoading] = useState(false);

    // Node form
    const [nodeForm, setNodeForm] = useState({
        id: '',
        name: '',
        type: 'service',
        tier: 'backend',
        status: 'healthy',
        cpu_usage: 20,
        memory_usage: 30,
        latency: 50,
        rpm: 100,
        error_rate: 0.5,
        connection_pool_usage: 0,
        queue_depth: 0,
        centrality_score: 0
    });

    // Edge form
    const [edgeForm, setEdgeForm] = useState({
        source: '',
        target: '',
        type: 'http',
        latency: 5,
        throughput: 100
    });

    const showMessage = (type: 'success' | 'error', text: string) => {
        setMessage({ type, text });
        setTimeout(() => setMessage(null), 5000);
    };

    const loadSystemData = async () => {
        try {
            const data = await api.getSystem();
            setSystemData(data);

            // Transform for React Flow
            const flowNodes = data.nodes.map((n: any, idx: number) => ({
                id: n.id,
                position: {
                    x: (idx % 5) * 200 + 100,
                    y: Math.floor(idx / 5) * 150 + 100
                },
                data: {
                    label: (
                        <div className="text-center">
                            <div className="font-semibold">{n.name}</div>
                            <div className="text-xs text-gray-400">{n.type}</div>
                        </div>
                    )
                },
                style: {
                    background: n.status === 'critical' ? '#ef4444' :
                        n.status === 'degraded' ? '#f59e0b' : '#1e1e2e',
                    color: '#fff',
                    border: '2px solid #3b82f6',
                    width: 160,
                    borderRadius: '12px',
                    padding: '12px'
                },
            }));

            const flowEdges = data.edges.map((e: any, i: number) => ({
                id: `e-${i}`,
                source: e.source,
                target: e.target,
                animated: true,
                style: { stroke: '#3b82f6', strokeWidth: 2 },
                label: e.type,
            }));

            setNodes(flowNodes);
            setEdges(flowEdges);
        } catch (error) {
            console.error('Failed to load system:', error);
        }
    };

    useEffect(() => {
        loadSystemData();
    }, []);

    const handleAddNode = async () => {
        try {
            setLoading(true);
            await api.addNode(nodeForm);
            showMessage('success', `Node "${nodeForm.name}" added!`);
            setNodeForm({
                id: '',
                name: '',
                type: 'service',
                tier: 'backend',
                status: 'healthy',
                cpu_usage: 20,
                memory_usage: 30,
                latency: 50,
                rpm: 100,
                error_rate: 0.5,
                connection_pool_usage: 0,
                queue_depth: 0,
                centrality_score: 0
            });
            await loadSystemData();
        } catch (error: any) {
            showMessage('error', error.message || 'Failed to add node');
        } finally {
            setLoading(false);
        }
    };

    const handleAddEdge = async () => {
        try {
            setLoading(true);
            await api.addEdge(edgeForm);
            showMessage('success', `Edge added!`);
            setEdgeForm({
                source: '',
                target: '',
                type: 'http',
                latency: 5,
                throughput: 100
            });
            await loadSystemData();
        } catch (error: any) {
            showMessage('error', error.message || 'Failed to add edge');
        } finally {
            setLoading(false);
        }
    };

    const handleLoadSample = async () => {
        if (!confirm('Load sample data? This will replace your current system.')) return;
        try {
            setLoading(true);
            await api.reset();
            showMessage('success', 'Sample data loaded!');
            await loadSystemData();
        } catch (error: any) {
            showMessage('error', 'Failed to load sample');
        } finally {
            setLoading(false);
        }
    };

    const handleClearAll = async () => {
        if (!confirm('Clear ALL nodes and edges?')) return;
        try {
            setLoading(true);
            await api.clearSystem();
            showMessage('success', 'System cleared!');
            await loadSystemData();
        } catch (error: any) {
            showMessage('error', 'Failed to clear system');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="h-full w-full flex p-6 gap-4">
            {/* Left Panel - Visualization */}
            <div className="flex-1 flex flex-col">
                <div className="flex justify-between items-center mb-4">
                    <div>
                        <h1 className="text-3xl font-bold mb-1">Architecture Explorer</h1>
                        <p className="text-gray-400">Visualize and manage your system topology</p>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={loadSystemData}
                            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                        >
                            <RefreshCw size={16} /> Refresh
                        </button>
                        <div className="bg-white/5 p-1 rounded-lg flex gap-1 border border-white/10">
                            <button
                                onClick={() => setViewMode('2d')}
                                className={`px-3 py-2 rounded-md flex items-center gap-2 transition-colors ${viewMode === '2d' ? 'bg-primary text-white' : 'hover:bg-white/5 text-gray-400'}`}
                            >
                                <Layers size={16} /> 2D
                            </button>
                            <button
                                onClick={() => setViewMode('3d')}
                                className={`px-3 py-2 rounded-md flex items-center gap-2 transition-colors ${viewMode === '3d' ? 'bg-primary text-white' : 'hover:bg-white/5 text-gray-400'}`}
                            >
                                <Box size={16} /> 3D
                            </button>
                        </div>
                        <button
                            onClick={() => setShowInputPanel(!showInputPanel)}
                            className={`px-3 py-2 rounded-lg flex items-center gap-2 transition-colors ${showInputPanel ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                        >
                            <Plus size={16} /> {showInputPanel ? 'Hide' : 'Add'} Nodes
                        </button>
                    </div>
                </div>

                {message && (
                    <div className={`mb-4 p-3 rounded-lg ${message.type === 'success' ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'
                        }`}>
                        {message.text}
                    </div>
                )}

                <div className="flex-1 glass-panel rounded-2xl overflow-hidden relative">
                    {systemData && systemData.nodes.length === 0 ? (
                        <div className="h-full flex items-center justify-center">
                            <div className="text-center">
                                <div className="text-4xl mb-4">🏗️</div>
                                <div className="text-xl text-gray-300 mb-2">No System Data</div>
                                <div className="text-gray-500 mb-4">Add nodes and edges to visualize your architecture</div>
                                <button
                                    onClick={() => setShowInputPanel(true)}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                >
                                    Start Building
                                </button>
                            </div>
                        </div>
                    ) : viewMode === '2d' ? (
                        <ReactFlow
                            nodes={nodes}
                            edges={edges}
                            onNodesChange={onNodesChange}
                            onEdgesChange={onEdgesChange}
                            fitView
                        >
                            <Background color="#444" gap={20} />
                            <Controls />
                            <MiniMap style={{ background: '#12121e' }} nodeColor={() => '#3b82f6'} />
                        </ReactFlow>
                    ) : (
                        <div className="w-full h-full bg-black/40">
                            <Canvas camera={{ position: [0, 0, 20], fov: 60 }}>
                                <ambientLight intensity={0.5} />
                                <pointLight position={[10, 10, 10]} />
                                <OrbitControls />
                                <System3D system={systemData} />
                            </Canvas>
                        </div>
                    )}
                </div>
            </div>

            {/* Right Panel - Input Controls */}
            {showInputPanel && (
                <div className="w-96 flex flex-col gap-4">
                    {/* Quick Actions */}
                    <div className="glass-panel rounded-xl p-4">
                        <h3 className="text-lg font-semibold text-white mb-3">Quick Actions</h3>
                        <div className="flex flex-col gap-2">
                            <button
                                onClick={handleLoadSample}
                                disabled={loading}
                                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2 disabled:bg-gray-700"
                            >
                                <Upload size={16} /> Load Sample Data
                            </button>
                            <button
                                onClick={handleClearAll}
                                disabled={loading}
                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2 disabled:bg-gray-700"
                            >
                                <Trash2 size={16} /> Clear All
                            </button>
                        </div>
                    </div>

                    {/* Add Node Form */}
                    <div className="glass-panel rounded-xl p-4 flex-1 overflow-y-auto">
                        <h3 className="text-lg font-semibold text-white mb-3">Add Service Node</h3>
                        <div className="space-y-3">
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">ID *</label>
                                <input
                                    type="text"
                                    value={nodeForm.id}
                                    onChange={(e) => setNodeForm({ ...nodeForm, id: e.target.value })}
                                    className="w-full bg-gray-800 text-gray-300 px-3 py-2 rounded text-sm"
                                    placeholder="e.g., api-server"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Name *</label>
                                <input
                                    type="text"
                                    value={nodeForm.name}
                                    onChange={(e) => setNodeForm({ ...nodeForm, name: e.target.value })}
                                    className="w-full bg-gray-800 text-gray-300 px-3 py-2 rounded text-sm"
                                    placeholder="e.g., API Server"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-2">
                                <div>
                                    <label className="block text-xs text-gray-400 mb-1">Type</label>
                                    <select
                                        value={nodeForm.type}
                                        onChange={(e) => setNodeForm({ ...nodeForm, type: e.target.value })}
                                        className="w-full bg-gray-800 text-gray-300 px-3 py-2 rounded text-sm"
                                    >
                                        <option value="service">Service</option>
                                        <option value="database">Database</option>
                                        <option value="cache">Cache</option>
                                        <option value="gateway">Gateway</option>
                                        <option value="external">External</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-xs text-gray-400 mb-1">Tier</label>
                                    <select
                                        value={nodeForm.tier}
                                        onChange={(e) => setNodeForm({ ...nodeForm, tier: e.target.value })}
                                        className="w-full bg-gray-800 text-gray-300 px-3 py-2 rounded text-sm"
                                    >
                                        <option value="frontend">Frontend</option>
                                        <option value="backend">Backend</option>
                                        <option value="data">Data</option>
                                        <option value="external">External</option>
                                    </select>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-2">
                                <div>
                                    <label className="block text-xs text-gray-400 mb-1">CPU %</label>
                                    <input
                                        type="number"
                                        value={nodeForm.cpu_usage}
                                        onChange={(e) => setNodeForm({ ...nodeForm, cpu_usage: parseFloat(e.target.value) })}
                                        className="w-full bg-gray-800 text-gray-300 px-3 py-2 rounded text-sm"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-gray-400 mb-1">Memory %</label>
                                    <input
                                        type="number"
                                        value={nodeForm.memory_usage}
                                        onChange={(e) => setNodeForm({ ...nodeForm, memory_usage: parseFloat(e.target.value) })}
                                        className="w-full bg-gray-800 text-gray-300 px-3 py-2 rounded text-sm"
                                    />
                                </div>
                            </div>
                            <button
                                onClick={handleAddNode}
                                disabled={loading || !nodeForm.id || !nodeForm.name}
                                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                <Plus size={16} /> Add Node
                            </button>
                        </div>

                        <hr className="my-4 border-white/10" />

                        <h3 className="text-lg font-semibold text-white mb-3">Add Dependency</h3>
                        <div className="space-y-3">
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Source Node ID *</label>
                                <input
                                    type="text"
                                    value={edgeForm.source}
                                    onChange={(e) => setEdgeForm({ ...edgeForm, source: e.target.value })}
                                    className="w-full bg-gray-800 text-gray-300 px-3 py-2 rounded text-sm"
                                    placeholder="e.g., web-app"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Target Node ID *</label>
                                <input
                                    type="text"
                                    value={edgeForm.target}
                                    onChange={(e) => setEdgeForm({ ...edgeForm, target: e.target.value })}
                                    className="w-full bg-gray-800 text-gray-300 px-3 py-2 rounded text-sm"
                                    placeholder="e.g., api-server"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-400 mb-1">Type</label>
                                <select
                                    value={edgeForm.type}
                                    onChange={(e) => setEdgeForm({ ...edgeForm, type: e.target.value })}
                                    className="w-full bg-gray-800 text-gray-300 px-3 py-2 rounded text-sm"
                                >
                                    <option value="http">HTTP</option>
                                    <option value="tcp">TCP</option>
                                    <option value="grpc">gRPC</option>
                                    <option value="async">Async</option>
                                </select>
                            </div>
                            <button
                                onClick={handleAddEdge}
                                disabled={loading || !edgeForm.source || !edgeForm.target}
                                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                <Plus size={16} /> Add Edge
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const System3D = ({ system }: { system: any }) => {
    if (!system) return null;

    // Simple 3D layout logic
    const nodes = system.nodes;
    const count = nodes.length;

    return (
        <group>
            {nodes.map((node: any, i: number) => {
                const angle = (i / count) * Math.PI * 2;
                const radius = 8;
                const x = Math.cos(angle) * radius;
                const z = Math.sin(angle) * radius;

                return (
                    <group key={node.id} position={[x, 0, z]}>
                        <mesh>
                            <sphereGeometry args={[0.8, 32, 32]} />
                            <meshStandardMaterial
                                color={node.status === 'critical' ? '#ef4444' : '#3b82f6'}
                                emissive={node.status === 'critical' ? '#ef4444' : '#3b82f6'}
                                emissiveIntensity={0.5}
                            />
                        </mesh>
                        <Text
                            position={[0, 1.2, 0]}
                            fontSize={0.5}
                            color="white"
                            anchorX="center"
                            anchorY="middle"
                        >
                            {node.name}
                        </Text>
                        {/* Draw lines to dependencies? A bit complex for simple layout, skipping for now */}
                    </group>
                );
            })}
            {/* Lines */}
            {system.edges.map((edge: any, i: number) => {
                const sourceIdx = nodes.findIndex((n: any) => n.id === edge.source);
                const targetIdx = nodes.findIndex((n: any) => n.id === edge.target);

                if (sourceIdx === -1 || targetIdx === -1) return null;

                const angleS = (sourceIdx / count) * Math.PI * 2;
                const xS = Math.cos(angleS) * 8;
                const zS = Math.sin(angleS) * 8;

                const angleT = (targetIdx / count) * Math.PI * 2;
                const xT = Math.cos(angleT) * 8;
                const zT = Math.sin(angleT) * 8;

                return (
                    <line key={i}>
                        <bufferGeometry>
                            <bufferAttribute
                                attach="attributes-position"
                                args={[new Float32Array([xS, 0, zS, xT, 0, zT]), 3]}
                            />
                        </bufferGeometry>
                        <lineBasicMaterial color="#ffffff30" transparent opacity={0.3} />
                    </line>
                )
            })}
        </group>
    );
};

export default ArchitectureHelper;
