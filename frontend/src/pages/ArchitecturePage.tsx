import { useState, useEffect } from 'react';
import ReactFlow, { Background, Controls, MiniMap, useNodesState, useEdgesState } from 'reactflow';
import 'reactflow/dist/style.css';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
import { api } from '../utils/api';
import { Layers, Box } from 'lucide-react';

const ArchitectureHelper = () => {
    const [viewMode, setViewMode] = useState<'2d' | '3d'>('2d');
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [systemData, setSystemData] = useState<any>(null);

    useEffect(() => {
        api.getSystem().then(data => {
            setSystemData(data);

            // Transform for React Flow
            const flowNodes = data.nodes.map((n: any) => ({
                id: n.id,
                position: { x: Math.random() * 800, y: Math.random() * 600 },
                data: { label: n.name },
                style: {
                    background: n.status === 'critical' ? '#ef4444' : '#1e1e2e',
                    color: '#fff',
                    border: '1px solid #ffffff20',
                    width: 150,
                    borderRadius: '8px',
                    padding: '10px'
                },
            }));

            const flowEdges = data.edges.map((e: any, i: number) => ({
                id: `e-${i}`,
                source: e.source,
                target: e.target,
                animated: true,
                style: { stroke: '#3b82f6' },
            }));

            setNodes(flowNodes);
            setEdges(flowEdges);
        });
    }, []);

    return (
        <div className="h-full w-full flex flex-col p-6">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Architecture Explorer</h1>
                    <p className="text-gray-400"> visualize system topology and dependencies.</p>
                </div>
                <div className="bg-white/5 p-1 rounded-lg flex gap-1 border border-white/10">
                    <button
                        onClick={() => setViewMode('2d')}
                        className={`px-4 py-2 rounded-md flex items-center gap-2 transition-colors ${viewMode === '2d' ? 'bg-primary text-white' : 'hover:bg-white/5 text-gray-400'}`}
                    >
                        <Layers size={18} /> 2D Graph
                    </button>
                    <button
                        onClick={() => setViewMode('3d')}
                        className={`px-4 py-2 rounded-md flex items-center gap-2 transition-colors ${viewMode === '3d' ? 'bg-primary text-white' : 'hover:bg-white/5 text-gray-400'}`}
                    >
                        <Box size={18} /> 3D Space
                    </button>
                </div>
            </div>

            <div className="flex-1 glass-panel rounded-2xl overflow-hidden relative">
                {viewMode === '2d' ? (
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
