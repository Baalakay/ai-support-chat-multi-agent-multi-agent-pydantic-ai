import React from 'react';

interface GridProps {
    children: React.ReactNode;
    columns?: number;
    className?: string;
}

export function Grid({ children, columns = 3, className = '' }: GridProps) {
    return (
        <div 
            className={`grid gap-4 ${className}`}
            style={{
                gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`
            }}
        >
            {children}
        </div>
    );
} 