import { LineChart } from './LineChart';
import { BarChart } from './BarChart';
import { Gauge } from './Gauge';

export interface ChartProps {
    data: number[];
    title: string;
    yLabel: string;
    className?: string;
}

export interface GaugeProps {
    value: number;
    title: string;
    max: number;
    className?: string;
}

export { LineChart, BarChart, Gauge }; 