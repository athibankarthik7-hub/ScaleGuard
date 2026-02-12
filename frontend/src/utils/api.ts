const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
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
    reset: async () => {
        const response = await fetch(`${API_BASE_URL}/reset`, { method: 'POST' });
        return response.json();
    }
};
