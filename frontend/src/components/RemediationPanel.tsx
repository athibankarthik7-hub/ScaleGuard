import { useEffect, useState } from 'react';
import { api } from '../utils/api';
import { Wrench, Play, Power, CheckCircle, XCircle, Clock, Activity, Shield } from 'lucide-react';

interface RemediationRule {
    rule_id: string;
    name: string;
    condition: string;
    action_type: string;
    enabled: boolean;
    auto_approve: boolean;
    cooldown_minutes: number;
    last_executed: string | null;
}

interface RemediationAction {
    action_id: string;
    service_id: string;
    action_type: string;
    reason: string;
    status: string;
    timestamp: string;
    execution_time?: string;
    details?: string;
}

interface Statistics {
    total_actions: number;
    completed: number;
    failed: number;
    pending: number;
    success_rate: number;
    actions_by_type: Record<string, number>;
    enabled: boolean;
    dry_run_mode: boolean;
    active_rules: number;
}

const RemediationPanel = () => {
    const [rules, setRules] = useState<RemediationRule[]>([]);
    const [actions, setActions] = useState<RemediationAction[]>([]);
    const [stats, setStats] = useState<Statistics | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const [rulesData, actionsData, statsData] = await Promise.all([
                api.getRemediationRules(),
                api.getRemediationActions(24),
                api.getRemediationStatistics()
            ]);
            setRules(rulesData.rules || []);
            setActions(actionsData.actions || []);
            setStats(statsData);
        } catch (error) {
            console.error('Failed to fetch remediation data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000); // Update every 10s
        return () => clearInterval(interval);
    }, []);

    const toggleRule = async (ruleId: string, enabled: boolean) => {
        try {
            await api.toggleRemediationRule(ruleId, enabled);
            await fetchData();
        } catch (error) {
            console.error('Failed to toggle rule:', error);
        }
    };

    const toggleSystem = async () => {
        try {
            await api.toggleAutoRemediation(!stats?.enabled);
            await fetchData();
        } catch (error) {
            console.error('Failed to toggle system:', error);
        }
    };

    const toggleDryRun = async () => {
        try {
            await api.toggleDryRunMode(!stats?.dry_run_mode);
            await fetchData();
        } catch (error) {
            console.error('Failed to toggle dry-run:', error);
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed': return <CheckCircle className="w-4 h-4 text-green-400" />;
            case 'failed': return <XCircle className="w-4 h-4 text-red-400" />;
            case 'executing': return <Activity className="w-4 h-4 text-blue-400 animate-pulse" />;
            case 'pending': return <Clock className="w-4 h-4 text-yellow-400" />;
            default: return <Clock className="w-4 h-4 text-gray-400" />;
        }
    };

    const getActionTypeColor = (type: string) => {
        const colors: Record<string, string> = {
            'scale_horizontal': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
            'restart_service': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
            'circuit_breaker': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
            'rate_limit': 'bg-green-500/20 text-green-400 border-green-500/30',
            'cache_clear': 'bg-pink-500/20 text-pink-400 border-pink-500/30',
        };
        return colors[type] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    };

    if (loading) {
        return (
            <div className="glass-panel rounded-2xl p-6">
                <div className="animate-pulse space-y-4">
                    <div className="h-6 bg-white/10 rounded w-1/3"></div>
                    <div className="h-32 bg-white/5 rounded-xl"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Control Panel */}
            <div className="glass-panel rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <Wrench className="w-6 h-6 text-green-400" />
                        <h3 className="text-xl font-bold">Auto-Remediation Control</h3>
                    </div>
                    <div className="flex gap-3">
                        <button
                            onClick={toggleDryRun}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${stats?.dry_run_mode
                                    ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                                }`}
                        >
                            <Shield className="w-4 h-4" />
                            {stats?.dry_run_mode ? 'Dry-Run ON' : 'Dry-Run OFF'}
                        </button>
                        <button
                            onClick={toggleSystem}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${stats?.enabled
                                    ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                                    : 'bg-red-500/20 text-red-400 border border-red-500/30'
                                }`}
                        >
                            <Power className="w-4 h-4" />
                            {stats?.enabled ? 'System ON' : 'System OFF'}
                        </button>
                    </div>
                </div>

                {/* Statistics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-black/20 rounded-xl p-4 border border-white/5">
                        <div className="text-3xl font-bold text-blue-400">{stats?.total_actions || 0}</div>
                        <div className="text-sm text-gray-400 mt-1">Total Actions</div>
                    </div>
                    <div className="bg-black/20 rounded-xl p-4 border border-white/5">
                        <div className="text-3xl font-bold text-green-400">{stats?.completed || 0}</div>
                        <div className="text-sm text-gray-400 mt-1">Completed</div>
                    </div>
                    <div className="bg-black/20 rounded-xl p-4 border border-white/5">
                        <div className="text-3xl font-bold text-yellow-400">{stats?.success_rate.toFixed(0) || 0}%</div>
                        <div className="text-sm text-gray-400 mt-1">Success Rate</div>
                    </div>
                    <div className="bg-black/20 rounded-xl p-4 border border-white/5">
                        <div className="text-3xl font-bold text-purple-400">{stats?.active_rules || 0}</div>
                        <div className="text-sm text-gray-400 mt-1">Active Rules</div>
                    </div>
                </div>
            </div>

            {/* Rules */}
            <div className="glass-panel rounded-2xl p-6">
                <h4 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <Shield className="w-5 h-5 text-blue-400" />
                    Remediation Rules
                </h4>
                <div className="space-y-3">
                    {rules.map((rule) => (
                        <div
                            key={rule.rule_id}
                            className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-all"
                        >
                            <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                    <h5 className="font-medium">{rule.name}</h5>
                                    <span className={`px-2 py-1 rounded text-xs border ${getActionTypeColor(rule.action_type)}`}>
                                        {rule.action_type.replace(/_/g, ' ')}
                                    </span>
                                    {rule.auto_approve && (
                                        <span className="px-2 py-1 rounded text-xs bg-green-500/20 text-green-400 border border-green-500/30">
                                            Auto-Approve
                                        </span>
                                    )}
                                </div>
                                <p className="text-sm text-gray-400">{rule.condition}</p>
                                <div className="flex gap-4 mt-2 text-xs text-gray-500">
                                    <span>Cooldown: {rule.cooldown_minutes}m</span>
                                    {rule.last_executed && (
                                        <span>Last: {new Date(rule.last_executed).toLocaleTimeString()}</span>
                                    )}
                                </div>
                            </div>
                            <button
                                onClick={() => toggleRule(rule.rule_id, !rule.enabled)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${rule.enabled
                                        ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                                        : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
                                    }`}
                            >
                                {rule.enabled ? 'Enabled' : 'Disabled'}
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Recent Actions */}
            <div className="glass-panel rounded-2xl p-6">
                <h4 className="text-lg font-bold mb-4 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-purple-400" />
                    Recent Actions (24h)
                </h4>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                    {actions.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                            <CheckCircle className="w-12 h-12 mb-3 text-green-500" />
                            <p className="text-sm">No actions executed recently</p>
                        </div>
                    ) : (
                        actions.slice(0, 10).map((action) => (
                            <div
                                key={action.action_id}
                                className="flex items-start gap-4 p-4 rounded-xl bg-white/5 border border-white/5"
                            >
                                <div className="mt-1">
                                    {getStatusIcon(action.status)}
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-2">
                                        <h5 className="font-medium">{action.service_id}</h5>
                                        <span className={`px-2 py-1 rounded text-xs border ${getActionTypeColor(action.action_type)}`}>
                                            {action.action_type.replace(/_/g, ' ')}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-400 mb-2">{action.reason}</p>
                                    {action.details && (
                                        <p className="text-xs text-gray-500 bg-black/20 rounded p-2">{action.details}</p>
                                    )}
                                    <div className="text-xs text-gray-500 mt-2">
                                        {new Date(action.timestamp).toLocaleString()}
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default RemediationPanel;
