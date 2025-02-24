import { useState } from 'react';

interface AccordionProps {
  title: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

export function Accordion({ title, children, defaultOpen = false, className = '' }: AccordionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className={className}>
      <button
        className="w-full flex justify-between items-center py-2 bg-gray-50 hover:bg-gray-100 transition-colors duration-150 rounded-t-md"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="w-full px-4">
          {title}
        </div>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
          aria-hidden="true"
          data-slot="icon"
          className={`w-5 h-5 text-gray-500 transition-transform duration-200 transform ${
            isOpen ? 'rotate-180' : ''
          } mr-4`}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="m19.5 8.25-7.5 7.5-7.5-7.5"
          />
        </svg>
      </button>
      {isOpen && children}
    </div>
  );
} 