"""Pre-action enforcement through code."""
import functools
from typing import Any, Callable, TypeVar
from .errors import BlockedActionError

T = TypeVar('T')


class PreActionEnforcer:
    """Enforces pre-action protocol through code.
    
    This enforcer ensures that all required validation steps are completed
    before any action can be taken. It works by decorating functions that
    need enforcement.
    
    Usage:
        enforcer = PreActionEnforcer()
        
        @enforcer
        async def edit_file():
            # Will be blocked until pre-action complete
            pass
    """
    
    def __init__(self):
        """Initialize the enforcer."""
        self.validation_complete = False
        self.rules_fetched = False
        self.patterns_cited = False
        self.validation_shown = False
        self._validation_steps = []
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator that enforces pre-action protocol."""
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            if not self.validation_complete:
                # Force rule fetching
                if not self.rules_fetched:
                    self._validation_steps.append(
                        "Rules must be fetched first"
                    )
                    raise BlockedActionError(
                        "MUST fetch rules before any action.",
                        required_action="fetch_rules(['rule_name'])"
                    )
                
                # Force pattern citation
                if not self.patterns_cited:
                    self._validation_steps.append(
                        "Patterns must be cited"
                    )
                    raise BlockedActionError(
                        "MUST cite patterns before any action.",
                        required_action="cite_patterns(rules)"
                    )
                
                # Force validation display
                if not self.validation_shown:
                    self._validation_steps.append(
                        "Validation must be shown"
                    )
                    raise BlockedActionError(
                        "MUST show validation before any action.",
                        required_action="show_validation(patterns)"
                    )
                
                self.validation_complete = True
            
            return await func(*args, **kwargs)
        return wrapper
    
    def mark_rules_fetched(self) -> None:
        """Mark that rules have been fetched."""
        self.rules_fetched = True
        self._validation_steps.append("✓ Rules fetched")
    
    def mark_patterns_cited(self) -> None:
        """Mark that patterns have been cited."""
        self.patterns_cited = True
        self._validation_steps.append("✓ Patterns cited")
    
    def mark_validation_shown(self) -> None:
        """Mark that validation has been shown."""
        self.validation_shown = True
        self._validation_steps.append("✓ Validation shown")
    
    def reset(self) -> None:
        """Reset the enforcer state."""
        self.validation_complete = False
        self.rules_fetched = False
        self.patterns_cited = False
        self.validation_shown = False
        self._validation_steps.clear()
    
    def get_validation_steps(self) -> list[str]:
        """Get the list of validation steps and their status."""
        return self._validation_steps.copy()
    
    def is_ready(self) -> bool:
        """Check if all validation steps are complete."""
        return all([
            self.rules_fetched,
            self.patterns_cited,
            self.validation_shown
        ]) 