import React from 'react';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    ChartOptions
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

export interface LineChartProps {
    data: number[];
    title: string;
    yLabel: string;
    className?: string;
}

export function LineChart({ data, title, yLabel, className = '' }: LineChartProps) {
    const chartData = {
        labels: data.map((_, i) => {
            const time = new Date();
            time.setMinutes(time.getMinutes() - (data.length - i - 1));
            return time.toLocaleTimeString();
        }),
        datasets: [
            {
                label: title,
                data: data,
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                tension: 0.1
            }
        ]
    };

    const options: ChartOptions<'line'> = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top' as const,
            },
            title: {
                display: true,
                text: title
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: yLabel
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Time'
                }
            }
        },
        animation: {
            duration: 750,
            easing: 'easeInOutQuart'
        }
    };

    return (
        <div className={`h-64 ${className}`}>
            <Line data={chartData} options={options} />
        </div>
    );
} 