import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ChartOptions
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

export interface BarChartProps {
    data: number[];
    title: string;
    yLabel: string;
    className?: string;
}

export function BarChart({ data, title, yLabel, className = '' }: BarChartProps) {
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
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 1
            }
        ]
    };

    const options: ChartOptions<'bar'> = {
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
            <Bar data={chartData} options={options} />
        </div>
    );
} 