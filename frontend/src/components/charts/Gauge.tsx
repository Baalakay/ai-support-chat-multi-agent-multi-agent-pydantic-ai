import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend,
    ChartOptions
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
    ArcElement,
    Tooltip,
    Legend
);

export interface GaugeProps {
    value: number;
    title: string;
    max: number;
    className?: string;
}

export function Gauge({ value, title, max, className = '' }: GaugeProps) {
    const percentage = (value / max) * 100;
    const remaining = 100 - percentage;

    // Color based on percentage
    const getColor = (percent: number) => {
        if (percent < 60) return 'rgb(34, 197, 94)';  // Green
        if (percent < 80) return 'rgb(234, 179, 8)';  // Yellow
        return 'rgb(239, 68, 68)';  // Red
    };

    const chartData = {
        labels: ['Value', 'Remaining'],
        datasets: [
            {
                data: [percentage, remaining],
                backgroundColor: [
                    getColor(percentage),
                    'rgb(229, 231, 235)'  // Gray
                ],
                borderColor: [
                    getColor(percentage),
                    'rgb(229, 231, 235)'
                ],
                borderWidth: 1,
                circumference: 180,
                rotation: 270
            }
        ]
    };

    const options: ChartOptions<'doughnut'> = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            title: {
                display: true,
                text: title
            },
            tooltip: {
                callbacks: {
                    label: (context) => {
                        if (context.dataIndex === 0) {
                            return `${value.toFixed(1)} / ${max} (${percentage.toFixed(1)}%)`;
                        }
                        return '';
                    }
                }
            }
        },
        cutout: '75%'
    };

    return (
        <div className={`relative h-48 ${className}`}>
            <Doughnut data={chartData} options={options} />
            <div className="absolute bottom-8 left-0 right-0 text-center">
                <div className="text-2xl font-bold text-gray-700">
                    {percentage.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-500">
                    {value.toFixed(1)} / {max}
                </div>
            </div>
        </div>
    );
} 