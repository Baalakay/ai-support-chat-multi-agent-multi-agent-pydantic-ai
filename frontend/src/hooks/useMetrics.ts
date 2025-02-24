import { useState, useEffect } from 'react';
import { api } from '../services/api';

export interface CacheMetrics {
    hitRates: number[];
    responseTimes: number[];
    requests: number;
    hits: number;
    misses: number;
}

export interface AgentMetrics {
    errorRates: number[];
    responseTimes: number[];
    requests: number;
    errors: number;
}

export interface SystemMetrics {
    cpuPercent: number;
    memoryUsage: number;
    totalMemory: number;
    threadCount: number;
    openFiles: number;
    connections: number;
    uptime: number;
}

export interface MetricsState {
    cacheMetrics: CacheMetrics | null;
    agentMetrics: AgentMetrics | null;
    systemMetrics: SystemMetrics | null;
    isLoading: boolean;
    error: string | null;
}

const MAX_HISTORY_POINTS = 20;

export function useMetrics(refreshInterval = 5000) {
    const [state, setState] = useState<MetricsState>({
        cacheMetrics: null,
        agentMetrics: null,
        systemMetrics: null,
        isLoading: true,
        error: null
    });

    useEffect(() => {
        let mounted = true;
        let history = {
            hitRates: [] as number[],
            responseTimes: [] as number[],
            errorRates: [] as number[]
        };

        async function fetchMetrics() {
            try {
                const [cache, agents, system] = await Promise.all([
                    api.get('/admin/metrics/cache'),
                    api.get('/admin/metrics/agents'),
                    api.get('/admin/metrics/system')
                ]);

                // Update history
                history.hitRates.push(cache.hit_rate);
                history.responseTimes.push(cache.avg_response_time);
                history.errorRates.push(agents.error_rate);

                // Keep only last N points
                if (history.hitRates.length > MAX_HISTORY_POINTS) {
                    history.hitRates = history.hitRates.slice(-MAX_HISTORY_POINTS);
                    history.responseTimes = history.responseTimes.slice(-MAX_HISTORY_POINTS);
                    history.errorRates = history.errorRates.slice(-MAX_HISTORY_POINTS);
                }

                if (mounted) {
                    setState({
                        cacheMetrics: {
                            hitRates: history.hitRates,
                            responseTimes: history.responseTimes,
                            requests: cache.requests,
                            hits: cache.hits,
                            misses: cache.misses
                        },
                        agentMetrics: {
                            errorRates: history.errorRates,
                            responseTimes: agents.avg_response_time,
                            requests: agents.requests,
                            errors: agents.errors
                        },
                        systemMetrics: {
                            cpuPercent: system.cpu_percent,
                            memoryUsage: system.memory_usage,
                            totalMemory: system.total_memory || 1000,  // MB
                            threadCount: system.thread_count,
                            openFiles: system.open_files,
                            connections: system.connections,
                            uptime: system.uptime
                        },
                        isLoading: false,
                        error: null
                    });
                }
            } catch (e) {
                if (mounted) {
                    setState(prev => ({
                        ...prev,
                        isLoading: false,
                        error: e instanceof Error ? e.message : 'Failed to fetch metrics'
                    }));
                }
            }
        }

        fetchMetrics();
        const interval = setInterval(fetchMetrics, refreshInterval);

        return () => {
            mounted = false;
            clearInterval(interval);
        };
    }, [refreshInterval]);

    return state;
} 