"""Pattern Enforcer - Technical enforcement of coding patterns.

This package provides active enforcement of coding patterns through:
1. Pre-action validation
2. Pattern checking
3. Regression prevention
4. Active monitoring
"""

from .enforcer import PreActionEnforcer
from .validator import PatternValidator
from .preventer import RegressionPreventer
from .monitor import PatternMonitor
from .handler import ViolationHandler
from .integration import TechnicalEnforcement
from .errors import (
    BlockedActionError,
    PatternViolationError,
    ValidationError
)

__version__ = "1.0.0"
__all__ = [
    'PreActionEnforcer',
    'PatternValidator',
    'RegressionPreventer',
    'PatternMonitor',
    'ViolationHandler',
    'TechnicalEnforcement',
    'BlockedActionError',
    'PatternViolationError',
    'ValidationError'
] 