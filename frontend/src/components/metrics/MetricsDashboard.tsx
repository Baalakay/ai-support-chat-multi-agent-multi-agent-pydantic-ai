import React from 'react';
import { LineChart } from '../charts/LineChart';
import { BarChart } from '../charts/BarChart';
import { Gauge } from '../charts/Gauge';
import { Card } from '../ui/Card';
import { Grid } from '../ui/Grid';
import { useMetrics } from '../../hooks/useMetrics';
import { Spinner } from '../ui/spinner';

export function MetricsDashboard() {
    const { 
        cacheMetrics,
        agentMetrics,
        systemMetrics,
        isLoading,
        error 
    } = useMetrics();

    if (isLoading) {
        return (
            <div className="flex justify-center items-center h-64">
                <Spinner />
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                Error loading metrics: {error}
            </div>
        );
    }

    if (!cacheMetrics || !agentMetrics || !systemMetrics) {
        return (
            <div className="text-gray-500 text-center py-4">
                No metrics data available
            </div>
        );
    }

    return (
        <div className="p-4 space-y-4">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">System Performance</h1>
            
            <Grid columns={2}>
                {/* Cache Performance */}
                <Card title="Cache Performance" className="col-span-2">
                    <div className="grid grid-cols-2 gap-4">
                        <LineChart
                            data={cacheMetrics.hitRates}
                            title="Cache Hit Rates"
                            yLabel="Hit Rate %"
                        />
                        <BarChart
                            data={cacheMetrics.responseTimes}
                            title="Response Times"
                            yLabel="ms"
                        />
                    </div>
                    <div className="mt-4 grid grid-cols-3 gap-4 text-center">
                        <div>
                            <div className="text-sm font-medium text-gray-500">Total Requests</div>
                            <div className="mt-1 text-2xl font-semibold text-gray-900">
                                {cacheMetrics.requests}
                            </div>
                        </div>
                        <div>
                            <div className="text-sm font-medium text-gray-500">Cache Hits</div>
                            <div className="mt-1 text-2xl font-semibold text-green-600">
                                {cacheMetrics.hits}
                            </div>
                        </div>
                        <div>
                            <div className="text-sm font-medium text-gray-500">Cache Misses</div>
                            <div className="mt-1 text-2xl font-semibold text-red-600">
                                {cacheMetrics.misses}
                            </div>
                        </div>
                    </div>
                </Card>

                {/* Agent Performance */}
                <Card title="Agent Performance">
                    <LineChart
                        data={agentMetrics.errorRates}
                        title="Error Rates"
                        yLabel="Error %"
                    />
                    <div className="mt-4 grid grid-cols-2 gap-4 text-center">
                        <div>
                            <div className="text-sm font-medium text-gray-500">Total Requests</div>
                            <div className="mt-1 text-2xl font-semibold text-gray-900">
                                {agentMetrics.requests}
                            </div>
                        </div>
                        <div>
                            <div className="text-sm font-medium text-gray-500">Total Errors</div>
                            <div className="mt-1 text-2xl font-semibold text-red-600">
                                {agentMetrics.errors}
                            </div>
                        </div>
                    </div>
                </Card>

                {/* System Resources */}
                <Card title="System Resources">
                    <div className="grid grid-cols-2 gap-4">
                        <Gauge
                            value={systemMetrics.cpuPercent}
                            title="CPU Usage"
                            max={100}
                        />
                        <Gauge
                            value={systemMetrics.memoryUsage}
                            title="Memory Usage (MB)"
                            max={systemMetrics.totalMemory}
                        />
                    </div>
                    <div className="mt-4 grid grid-cols-3 gap-4 text-center">
                        <div>
                            <div className="text-sm font-medium text-gray-500">Threads</div>
                            <div className="mt-1 text-xl font-semibold text-gray-900">
                                {systemMetrics.threadCount}
                            </div>
                        </div>
                        <div>
                            <div className="text-sm font-medium text-gray-500">Open Files</div>
                            <div className="mt-1 text-xl font-semibold text-gray-900">
                                {systemMetrics.openFiles}
                            </div>
                        </div>
                        <div>
                            <div className="text-sm font-medium text-gray-500">Connections</div>
                            <div className="mt-1 text-xl font-semibold text-gray-900">
                                {systemMetrics.connections}
                            </div>
                        </div>
                    </div>
                </Card>
            </Grid>
        </div>
    );
} 