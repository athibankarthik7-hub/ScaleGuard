import { useState, useEffect } from 'react';
import { Brain, Settings, Check } from 'lucide-react';
import { api } from '../utils/api';

interface AIProvider {
    providers: string[];
    current: string;
}

const AIProviderSwitcher = () => {
    const [providers, setProviders] = useState<AIProvider | null>(null);
    const [loading, setLoading] = useState(false);
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        fetchProviders();
    }, []);

    const fetchProviders = async () => {
        try {
            const data = await api.getAIProviders();
            setProviders(data);
        } catch (e) {
            console.error("Failed to fetch AI providers", e);
        }
    };

    const switchProvider = async (provider: string) => {
        setLoading(true);
        try {
            await api.switchAIProvider(provider);
            await fetchProviders();
            setIsOpen(false);
        } catch (e) {
            console.error("Failed to switch AI provider", e);
        } finally {
            setLoading(false);
        }
    };

    const getProviderDisplayName = (provider: string) => {
        switch (provider) {
            case 'openai': return 'OpenAI GPT-4';
            case 'gemini': return 'Google Gemini';
            case 'claude': return 'Anthropic Claude';
            case 'mock': return 'Mock Provider';
            case 'jarvis': return 'JARVIS';
            default: return provider;
        }
    };

    const getProviderColor = (provider: string) => {
        switch (provider) {
            case 'openai': return 'text-green-400';
            case 'gemini': return 'text-blue-400';
            case 'claude': return 'text-purple-400';
            case 'mock': return 'text-amber-400';
            case 'jarvis': return 'text-cyan-400';
            default: return 'text-white';
        }
    };

    if (!providers) return null;

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-3 py-2 bg-black/25 border border-white/10 rounded-lg hover:border-white/20 transition-colors min-w-0 w-full lg:w-auto"
                disabled={loading}
            >
                <Brain size={14} className={getProviderColor(providers.current)} />
                <span className="text-xs lg:text-sm font-medium text-white">
                    <span className="hidden lg:inline">{getProviderDisplayName(providers.current)}</span>
                    <span className="lg:hidden">AI</span>
                </span>
                <Settings size={12} className="text-gray-400" />
            </button>

            {isOpen && (
                <div className="absolute bottom-full left-0 mb-2 w-56 bg-black/95 border border-white/20 rounded-lg shadow-xl backdrop-blur-sm z-[100]">
                    <div className="p-2 max-h-60 overflow-y-auto">
                        <div className="text-xs text-gray-400 px-3 py-2 border-b border-white/20 mb-1">
                            AI Provider Selection
                        </div>
                        {providers.providers.map((provider) => (
                            <button
                                key={provider}
                                onClick={() => switchProvider(provider)}
                                disabled={loading || provider === providers.current}
                                className="w-full flex items-center gap-3 px-3 py-2 mt-1 rounded-lg hover:bg-white/10 transition-colors text-left disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                <Brain size={14} className={getProviderColor(provider)} />
                                <span className="flex-1 text-sm text-white">
                                    {getProviderDisplayName(provider)}
                                </span>
                                {provider === providers.current && (
                                    <Check size={14} className="text-green-400" />
                                )}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Click outside to close */}
            {isOpen && (
                <div
                    className="fixed inset-0 z-[90]"
                    onClick={() => setIsOpen(false)}
                />
            )}
        </div>
    );
};

export default AIProviderSwitcher;