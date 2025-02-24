import { Card } from './Card';
import { Grid } from './Grid';
import { Spinner } from './spinner';

export interface CardProps {
    title: string;
    children: React.ReactNode;
    className?: string;
}

export interface GridProps {
    children: React.ReactNode;
    columns?: number;
    className?: string;
}

export { Card, Grid, Spinner }; 