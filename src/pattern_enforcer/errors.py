"""Error classes for pattern enforcement."""

class PatternEnforcerError(Exception):
    """Base error for pattern enforcer."""
    pass


class BlockedActionError(PatternEnforcerError):
    """Error raised when an action is blocked due to missing validation."""
    
    def __init__(self, message: str, required_action: str = None):
        self.required_action = required_action
        super().__init__(
            f"{message}\n"
            f"Required action: {required_action}" if required_action else message
        )


class PatternViolationError(PatternEnforcerError):
    """Error raised when a pattern violation is detected."""
    
    def __init__(self, message: str, violations: list[str] = None):
        self.violations = violations or []
        super().__init__(
            f"{message}\n"
            f"Violations:\n" + "\n".join(f"- {v}" for v in self.violations)
            if self.violations else message
        )


class ValidationError(PatternEnforcerError):
    """Error raised when validation fails."""
    
    def __init__(self, message: str, validation_errors: list[str] = None):
        self.validation_errors = validation_errors or []
        super().__init__(
            f"{message}\n"
            f"Validation errors:\n" + "\n".join(f"- {e}" for e in self.validation_errors)
            if self.validation_errors else message
        ) 