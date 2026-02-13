const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
    // Core System APIs
    getSystem: async () => {
        const response = await fetch(`${API_BASE_URL}/system`);
        return response.json();
    },
    simulate: async (config: any) => {
        const response = await fetch(`${API_BASE_URL}/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        return response.json();
    },
    getRiskScore: async () => {
        const response = await fetch(`${API_BASE_URL}/risk-score`);
        return response.json();
    },
    getAnalysis: async () => {
        const response = await fetch(`${API_BASE_URL}/analysis`);
        return response.json();
    },
    getBottlenecks: async () => {
        const response = await fetch(`${API_BASE_URL}/bottlenecks`);
        return response.json();
    },
    reset: async () => {
        const response = await fetch(`${API_BASE_URL}/reset`, { method: 'POST' });
        return response.json();
    },

    // AI Provider APIs
    getAIProviders: async () => {
        const response = await fetch(`${API_BASE_URL}/ai/providers`);
        return response.json();
    },
    switchAIProvider: async (provider: string) => {
        const response = await fetch(`${API_BASE_URL}/ai/switch-provider?provider=${provider}`, {
            method: 'POST',
        });
        return response.json();
    },

    // Historical Tracking APIs
    getHistoricalTrends: async (timeWindowMinutes: number = 60) => {
        const response = await fetch(`${API_BASE_URL}/historical/trends?time_window_minutes=${timeWindowMinutes}`);
        return response.json();
    },
    getHistoricalSnapshots: async (minutes: number = 60) => {
        const response = await fetch(`${API_BASE_URL}/historical/snapshots?minutes=${minutes}`);
        return response.json();
    },
    getHistoricalStatistics: async () => {
        const response = await fetch(`${API_BASE_URL}/historical/statistics`);
        return response.json();
    },
    getServiceHistory: async (serviceId: string, minutes: number = 60) => {
        const response = await fetch(`${API_BASE_URL}/historical/service/${serviceId}?minutes=${minutes}`);
        return response.json();
    },

    // Predictive Analytics APIs
    getAllPredictions: async () => {
        const response = await fetch(`${API_BASE_URL}/predictions/all`);
        return response.json();
    },
    getFailurePredictions: async () => {
        const response = await fetch(`${API_BASE_URL}/predictions/failures`);
        return response.json();
    },
    getCascadePredictions: async () => {
        const response = await fetch(`${API_BASE_URL}/predictions/cascades`);
        return response.json();
    },

    // Auto-Remediation APIs
    getRemediationRules: async () => {
        const response = await fetch(`${API_BASE_URL}/remediation/rules`);
        return response.json();
    },
    getRemediationActions: async (hours: number = 24) => {
        const response = await fetch(`${API_BASE_URL}/remediation/actions?hours=${hours}`);
        return response.json();
    },
    getPendingRemediations: async () => {
        const response = await fetch(`${API_BASE_URL}/remediation/pending`);
        return response.json();
    },
    getActiveRemediations: async () => {
        const response = await fetch(`${API_BASE_URL}/remediation/active`);
        return response.json();
    },
    getRemediationStatistics: async () => {
        const response = await fetch(`${API_BASE_URL}/remediation/statistics`);
        return response.json();
    },
    executeRemediation: async (actionId: string) => {
        const response = await fetch(`${API_BASE_URL}/remediation/execute/${actionId}`, {
            method: 'POST',
        });
        return response.json();
    },
    toggleRemediationRule: async (ruleId: string, enabled: boolean) => {
        const response = await fetch(`${API_BASE_URL}/remediation/rules/${ruleId}/toggle?enabled=${enabled}`, {
            method: 'POST',
        });
        return response.json();
    },
    toggleAutoRemediation: async (enabled: boolean) => {
        const response = await fetch(`${API_BASE_URL}/remediation/toggle?enabled=${enabled}`, {
            method: 'POST',
        });
        return response.json();
    },
    toggleDryRunMode: async (dryRun: boolean) => {
        const response = await fetch(`${API_BASE_URL}/remediation/dry-run?dry_run=${dryRun}`, {
            method: 'POST',
        });
        return response.json();
    }
};
