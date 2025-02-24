"""AI Support Agent package.

Provides tools and services for AI-powered PDF analysis and comparison.
"""

# Configure logfire and auto-tracing before any other imports
import logfire
logfire.configure(
    service_name="ai_support_agent",
    environment="development"
)
logfire.install_auto_tracing(
    modules=['ai_support_agent'],  # This will catch all submodules including tests
    min_duration=0,  # Trace everything initially
    check_imported_modules='ignore'  # Allow tracing of already imported modules
)

# Core types first
from .types.pdf import PDFContent, PDFPage, PDFSection, PDFCategory, PDFSpecification
from .types.product import QueryIntent, QueryDomain

# Version info
__version__ = "0.1.0"
__all__ = [
    # Types
    'PDFContent',
    'PDFPage',
    'PDFSection',
    'PDFCategory',
    'PDFSpecification',
    'QueryIntent',
    'QueryDomain',
] 