"""Unit transformation and standardization tools."""

from typing import Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class UnitType(str, Enum):
    """Enumeration of unit types for standardization."""
    TEMPERATURE = "temperature"
    RESISTANCE = "resistance"
    VOLTAGE = "voltage"
    CURRENT = "current"
    POWER = "power"
    TIME = "time"
    FREQUENCY = "frequency"
    CAPACITANCE = "capacitance"
    INDUCTANCE = "inductance"
    VOLUME = "volume"
    MAGNETIC = "magnetic"  # Add magnetic type


class UnitStandard(BaseModel):
    """Standard representation of a unit."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    
    symbol: str = Field(..., min_length=1, description="Unit symbol (e.g., 'Ω', 'V')")
    display: str = Field(..., min_length=1, description="Display format (e.g., 'Ω', 'V')")
    type: UnitType = Field(..., description="Type of unit")
    suffixes: Dict[str, str] = Field(
        default_factory=lambda: {
            "maximum": "max",
            "minimum": "min",
            "typical": "typ",
            "nominal": "nom"
        },
        description="Map of full suffix to abbreviated form"
    )


class UnitTransformer:
    """Tool for standardizing units and their display format."""
    
    # Standard unit mappings
    STANDARD_UNITS: Dict[str, UnitStandard] = {
        # Temperature
        "°C": UnitStandard(
            symbol="°C",
            display="°C",
            type=UnitType.TEMPERATURE
        ),
        "°F": UnitStandard(
            symbol="°F",
            display="°F",
            type=UnitType.TEMPERATURE
        ),
        # Resistance
        "ohm": UnitStandard(
            symbol="Ω",
            display="Ω",
            type=UnitType.RESISTANCE
        ),
        "ohms": UnitStandard(
            symbol="Ω",
            display="Ω",
            type=UnitType.RESISTANCE
        ),
        "Ohm": UnitStandard(
            symbol="Ω",
            display="Ω",
            type=UnitType.RESISTANCE
        ),
        "Ohms": UnitStandard(
            symbol="Ω",
            display="Ω",
            type=UnitType.RESISTANCE
        ),
        # Voltage
        "V": UnitStandard(
            symbol="V",
            display="V",
            type=UnitType.VOLTAGE
        ),
        "VDC": UnitStandard(
            symbol="VDC",
            display="VDC",
            type=UnitType.VOLTAGE
        ),
        "VAC": UnitStandard(
            symbol="VAC",
            display="VAC",
            type=UnitType.VOLTAGE
        ),
        "Volts": UnitStandard(
            symbol="V",
            display="V",
            type=UnitType.VOLTAGE
        ),
        # Current
        "A": UnitStandard(
            symbol="A",
            display="A",
            type=UnitType.CURRENT
        ),
        "Amp": UnitStandard(
            symbol="A",
            display="A",
            type=UnitType.CURRENT
        ),
        "Amps": UnitStandard(
            symbol="A",
            display="A",
            type=UnitType.CURRENT
        ),
        "mA": UnitStandard(
            symbol="mA",
            display="mA",
            type=UnitType.CURRENT
        ),
        # Power
        "W": UnitStandard(
            symbol="W",
            display="W",
            type=UnitType.POWER
        ),
        "Watt": UnitStandard(
            symbol="W",
            display="W",
            type=UnitType.POWER
        ),
        "Watts": UnitStandard(
            symbol="W",
            display="W",
            type=UnitType.POWER
        ),
        # Time
        "ms": UnitStandard(
            symbol="ms",
            display="ms",
            type=UnitType.TIME
        ),
        "msec": UnitStandard(
            symbol="ms",
            display="ms",
            type=UnitType.TIME
        ),
        "msecs": UnitStandard(
            symbol="ms",
            display="ms",
            type=UnitType.TIME
        ),
        "mSeconds": UnitStandard(
            symbol="ms",
            display="ms",
            type=UnitType.TIME
        ),
        "millisecond": UnitStandard(
            symbol="ms",
            display="ms",
            type=UnitType.TIME
        ),
        "milliseconds": UnitStandard(
            symbol="ms",
            display="ms",
            type=UnitType.TIME
        ),
        "Milliseconds": UnitStandard(
            symbol="ms",
            display="ms",
            type=UnitType.TIME
        ),
        "MILLISECONDS": UnitStandard(
            symbol="ms",
            display="ms",
            type=UnitType.TIME
        ),
        # Volume
        "CC": UnitStandard(
            symbol="cc",
            display="cc",
            type=UnitType.VOLUME
        ),
        "cc": UnitStandard(
            symbol="cc",
            display="cc",
            type=UnitType.VOLUME
        ),
        "cubic centimeter": UnitStandard(
            symbol="cc",
            display="cc",
            type=UnitType.VOLUME
        ),
        "cubic centimeters": UnitStandard(
            symbol="cc",
            display="cc",
            type=UnitType.VOLUME
        ),
        "CUBIC CENTIMETERS": UnitStandard(
            symbol="cc",
            display="cc",
            type=UnitType.VOLUME
        ),
        "Cubic Centimeters": UnitStandard(
            symbol="cc",
            display="cc",
            type=UnitType.VOLUME
        ),
        "Cubic centimeters": UnitStandard(
            symbol="cc",
            display="cc",
            type=UnitType.VOLUME
        ),
        # Capacitance
        "pF": UnitStandard(
            symbol="pF",
            display="pF",
            type=UnitType.CAPACITANCE
        ),
        "picofarad": UnitStandard(
            symbol="pF",
            display="pF",
            type=UnitType.CAPACITANCE
        ),
        "picofarads": UnitStandard(
            symbol="pF",
            display="pF",
            type=UnitType.CAPACITANCE
        ),
        # Inductance
        "mH": UnitStandard(
            symbol="mH",
            display="mH",
            type=UnitType.INDUCTANCE
        ),
        "millihenry": UnitStandard(
            symbol="mH",
            display="mH",
            type=UnitType.INDUCTANCE
        ),
        "millihenries": UnitStandard(
            symbol="mH",
            display="mH",
            type=UnitType.INDUCTANCE
        ),
        # Magnetic
        "AT": UnitStandard(
            symbol="AT",
            display="AT",
            type=UnitType.MAGNETIC
        ),
        "Ampere Turn": UnitStandard(
            symbol="AT",
            display="AT",
            type=UnitType.MAGNETIC
        ),
        "Ampere Turns": UnitStandard(
            symbol="AT",
            display="AT",
            type=UnitType.MAGNETIC
        ),
        "ampere turn": UnitStandard(
            symbol="AT",
            display="AT",
            type=UnitType.MAGNETIC
        ),
        "ampere turns": UnitStandard(
            symbol="AT",
            display="AT",
            type=UnitType.MAGNETIC
        ),
        "AMPERE TURNS": UnitStandard(
            symbol="AT",
            display="AT",
            type=UnitType.MAGNETIC
        ),
    }

    @classmethod
    def standardize_unit(cls, unit: Optional[str]) -> Optional[str]:
        """Standardize a unit string.
        
        Args:
            unit: Unit string to standardize (e.g., "Ohms - maximum")
            
        Returns:
            Standardized unit string (e.g., "Ω - max") or None if no match
        """
        if not unit:
            return None

        # Step 1: Split into unit and suffix
        parts = [p.strip() for p in unit.split("-", 1)]
        base_unit = parts[0].strip()
        suffix = parts[1].strip() if len(parts) > 1 else None

        # Step 2: Get standard unit
        standard = None
        
        # Try all case variations
        variations = [
            base_unit,
            base_unit.lower(),
            base_unit.upper(),
            base_unit.capitalize(),
            base_unit.title()  # For "Cubic Centimeters"
        ]
        
        for variant in variations:
            standard = cls.STANDARD_UNITS.get(variant)
            if standard:
                break
                
        # If still no match, return original
        if not standard:
            return unit

        # Step 3: Format with standardized suffix
        if suffix:
            suffix_lower = suffix.lower()
            # Always abbreviate standard suffixes
            if suffix_lower in ["maximum", "minimum", "nominal", "typical"]:
                abbrev = suffix_lower[:3]  # max, min, nom, typ
                return f"{standard.display} - {abbrev}"
            # For any other suffix, keep it as is
            return f"{standard.display} - {suffix}"
        
        return standard.display

    @classmethod
    def format_display_value(cls, value: str, unit: Optional[str]) -> str:
        """Format a value with its unit for display.
        
        Args:
            value: The value to format
            unit: Optional unit string
            
        Returns:
            Formatted string for display
        """
        if not unit:
            return value
            
        # Handle special cases like temperature ranges
        if "to" in value:
            # For ranges like "-40 to +125"
            return f"{value} {unit}"
            
        # For normal values
        return f"{value} {unit}"