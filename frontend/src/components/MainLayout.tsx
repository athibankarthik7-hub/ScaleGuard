import { Outlet, NavLink } from 'react-router-dom';
import { LayoutDashboard, Network, PlayCircle, Activity, Upload } from 'lucide-react';
import AIProviderSwitcher from './AIProviderSwitcher';

const Layout = () => {
    return (
        <div className="flex h-screen w-screen bg-background overflow-hidden relative">
            {/* Background ambient glow */}
            <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary/20 blur-[120px] rounded-full pointer-events-none" />
            <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-accent/20 blur-[120px] rounded-full pointer-events-none" />

            {/* Sidebar */}
            <aside className="w-20 lg:w-64 glass-panel border-r border-white/10 z-10 flex flex-col">
                <div className="h-16 flex items-center justify-center lg:justify-start lg:px-6 border-b border-white/10">
                    <div className="w-8 h-8 bg-gradient-to-tr from-primary to-accent rounded-lg flex items-center justify-center shrink-0">
                        <Activity className="w-5 h-5 text-white" />
                    </div>
                    <span className="hidden lg:block ml-3 font-bold text-xl tracking-tight">ScaleGuard</span>
                </div>

                <nav className="flex-1 py-6 px-2 lg:px-4 space-y-2">
                    <NavItem to="/app" end icon={<LayoutDashboard />} label="Dashboard" />
                    <NavItem to="/app/architecture" icon={<Network />} label="Architecture" />
                    <NavItem to="/app/simulation" icon={<PlayCircle />} label="Simulation" />
                    <NavItem to="/app/incidents" icon={<Activity />} label="Incidents" />
                </nav>

                <div className="p-4 border-t border-white/10 space-y-3">
                    <AIProviderSwitcher />
                    <div className="flex items-center gap-3 text-xs text-gray-400">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="hidden lg:block">System Online</span>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto relative z-0">
                <Outlet />
            </main>
        </div>
    );
};

const NavItem = ({ to, icon, label, end = false }: { to: string, icon: React.ReactNode, label: string, end?: boolean }) => (
    <NavLink
        to={to}
        end={end}
        className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group ${isActive
                ? 'bg-primary/20 text-white shadow-lg shadow-primary/10 border border-primary/20'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`
        }
    >
        <span className="w-6 h-6 flex items-center justify-center group-hover:scale-110 transition-transform">{icon}</span>
        <span className="hidden lg:block font-medium">{label}</span>
    </NavLink>
);

export default Layout;
