"""Core type definitions."""
from .agent import AgentDependencies, DataLoaderDependencies, ProductSpecialistDependencies, CustomerSupportDependencies
from .pdf import PDFContent, PDFProcessingError
from .product import QueryIntent, QueryDomain, DisplayPreferences

__all__ = [
    'AgentDependencies',
    'DataLoaderDependencies',
    'ProductSpecialistDependencies',
    'CustomerSupportDependencies',
    'PDFContent',
    'PDFProcessingError',
    'QueryIntent',
    'QueryDomain',
    'DisplayPreferences'
]
