"""Difference processing module."""
from typing import Dict, List, Optional, Tuple
import pandas as pd
from ai_support_agent.types.differences import Differences, Difference


class DifferenceProcessor:
    """Processor for analyzing differences between models."""

    @staticmethod
    def analyze_differences(df: pd.DataFrame) -> Differences:
        """Analyze differences between model specifications."""
        differences = Differences()

        if df.empty:
            return differences

        # Get model columns (non-metadata columns)
        model_cols = [
            col for col in df.columns
            if col not in ["Category", "Specification"]
        ]

        # Process each row
        for _, row in df.iterrows():
            # Get model-specific values
            values = {
                model: str(row[model]).strip()
                for model in model_cols
                if str(row[model]).strip() and
                str(row[model]).lower() != 'nan'
            }

            if len(values) < 2:  # Skip if not enough models have values
                continue

            # Split specification into parts
            spec = row["Specification"]
            unit = None
            if "(" in spec and ")" in spec:
                # Extract unit from parentheses
                unit_start = spec.rfind("(")
                unit_end = spec.rfind(")")
                if unit_start > 0 and unit_end > unit_start:
                    unit = spec[unit_start + 1:unit_end].strip()
                    spec = spec[:unit_start].strip()

            # Split category and subcategory
            parts = spec.split(" - ", 1)
            subcategory = parts[1] if len(parts) > 1 else ""
            category = parts[0]

            # Add difference if values are actually different
            differences.add_difference(
                category=category,
                subcategory=subcategory,
                unit=unit,
                values=values
            )

        return differences

    @staticmethod
    def format_difference(
        diff: Difference,
        include_units: bool = True
    ) -> str:
        """Format a difference for display."""
        parts = []

        # Add category and subcategory
        if diff.subcategory:
            parts.append(f"{diff.category} - {diff.subcategory}")
        else:
            parts.append(diff.category)

        # Add values with units if requested
        values_str = []
        for model, value in diff.values.items():
            if include_units and diff.unit:
                values_str.append(f"{model}: {value} {diff.unit}")
            else:
                values_str.append(f"{model}: {value}")

        parts.append(", ".join(values_str))

        return ": ".join(parts)

    @staticmethod
    def summarize_differences(differences: Differences) -> str:
        """Create a summary of differences."""
        if not differences.has_differences():
            return "No significant differences found."

        summary_parts = []

        # Group differences by category
        by_category: Dict[str, List[Difference]] = {}
        for diff in differences.differences:
            if diff.category not in by_category:
                by_category[diff.category] = []
            by_category[diff.category].append(diff)

        # Create summary for each category
        for category, diffs in by_category.items():
            summary_parts.append(f"\n{category}:")
            for diff in diffs:
                summary_parts.append(
                    f"  - {DifferenceProcessor.format_difference(diff)}"
                )

        return "\n".join(summary_parts)
