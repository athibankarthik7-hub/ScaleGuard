import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere, MeshDistortMaterial } from '@react-three/drei';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Activity, Zap, Shield } from 'lucide-react';
import { motion } from 'framer-motion';

const AnimatedSphere = () => {
    const meshRef = useRef<any>(null);
    useFrame((state) => {
        if (meshRef.current) {
            meshRef.current.rotation.x = state.clock.getElapsedTime() * 0.2;
            meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.3;
        }
    });

    return (
        <Sphere visible args={[1, 100, 200]} scale={2.5} ref={meshRef}>
            <MeshDistortMaterial
                color="#3b82f6"
                attach="material"
                distort={0.4} // Strength, 0 disables the effect (default=1)
                speed={1.5} // Speed (default=1)
                roughness={0.2}
                metalness={0.9}
            />
        </Sphere>
    );
};

const LandingPage = () => {
    const navigate = useNavigate();

    return (
        <div className="relative w-full h-screen bg-background overflow-hidden flex flex-col items-center justify-center text-white">
            <div className="absolute inset-0 z-0 opacity-40">
                <Canvas>
                    <ambientLight intensity={0.5} />
                    <directionalLight position={[10, 10, 5]} intensity={1} />
                    <AnimatedSphere />
                    <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
                </Canvas>
            </div>

            <div className="z-10 text-center px-6 max-w-4xl relative">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <div className="flex items-center justify-center mb-6">
                        <div className="w-12 h-12 bg-gradient-to-tr from-primary to-accent rounded-2xl flex items-center justify-center shadow-lg shadow-primary/40">
                            <Activity className="w-7 h-7 text-white" />
                        </div>
                    </div>
                    <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 animate-pulse-slow">
                        ScaleGuard
                    </h1>
                    <p className="text-xl md:text-2xl text-gray-300 mb-10 leading-relaxed">
                        Predict where systems break before they do.
                        <br />
                        <span className="text-gray-500 text-lg">Next-gen root cause intelligence & scaling simulation.</span>
                    </p>

                    <div className="flex flex-col md:flex-row gap-4 justify-center">
                        <button
                            onClick={() => navigate('/app')}
                            className="group relative px-8 py-4 bg-white text-black font-semibold rounded-full text-lg hover:bg-gray-100 transition-all shadow-[0_0_20px_rgba(255,255,255,0.3)] hover:shadow-[0_0_30px_rgba(255,255,255,0.5)] flex items-center justify-center gap-2"
                        >
                            Launch Demo
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </button>
                        <button className="px-8 py-4 bg-white/5 border border-white/10 text-white font-semibold rounded-full text-lg hover:bg-white/10 transition-all backdrop-blur-md">
                            Read Manifesto
                        </button>
                    </div>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20">
                    <FeatureCard icon={<Zap className="text-yellow-400" />} title="Predictive Scaling" desc="Simulate traffic spikes and spot bottlenecks instantly." delay={0.2} />
                    <FeatureCard icon={<NetworkIcon className="text-blue-400" />} title="Visual Architecture" desc="Interactive 3D maps of your entire microservice galaxy." delay={0.4} />
                    <FeatureCard icon={<Shield className="text-green-400" />} title="Root Cause AI" desc="Trace failures back to origin with probabilistic ranking." delay={0.6} />
                </div>
            </div>
        </div>
    );
};

// Quick icon wrap
const NetworkIcon = (props: any) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="6" height="6" x="14" y="2" rx="1" /><rect width="6" height="6" x="4" y="16" rx="1" /><path d="M5 16v-2.5a2.5 2.5 0 0 1 5 0V16" /><path d="M19 19v-2.5a2.5 2.5 0 0 0-5 0V19" /><line x1="14" x2="14" y1="19" y2="8" /></svg>
)

const FeatureCard = ({ icon, title, desc, delay }: { icon: React.ReactNode, title: string, desc: string, delay: number }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay }}
        className="p-6 glass-card rounded-2xl text-left"
    >
        <div className="mb-4 w-10 h-10 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
            {icon}
        </div>
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-sm text-gray-400">{desc}</p>
    </motion.div>
);

export default LandingPage;
