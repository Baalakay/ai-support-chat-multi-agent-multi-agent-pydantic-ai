import { useState } from 'react';

interface DiagramThumbnailProps {
  imagePath: string;
  alt?: string;
  className?: string;
}

export function DiagramThumbnail({ 
  imagePath, 
  alt = 'Diagram', 
  className = ''
}: DiagramThumbnailProps) {
  const [error, setError] = useState(false);

  if (error) {
    return (
      <div className="text-sm text-gray-500 italic">
        Image not available
      </div>
    );
  }

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    window.open(imagePath, '_blank', 'noopener,noreferrer');
  };

  return (
    <a 
      href={imagePath} 
      target="_blank" 
      rel="noopener noreferrer"
      onClick={handleClick}
      className="block w-24 h-16 mx-auto"
    >
      <img
        src={imagePath}
        alt={alt}
        className={`w-full h-full hover:opacity-80 transition-opacity object-contain ${className}`}
        onError={() => setError(true)}
      />
    </a>
  );
} 