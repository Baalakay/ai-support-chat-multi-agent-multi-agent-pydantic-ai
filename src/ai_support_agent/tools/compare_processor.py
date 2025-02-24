"""Service for comparing PDF specifications."""

from typing import Dict, List, Optional, Any, Tuple
import uuid
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict

from ..types.pdf import PDFContent, PDFSection, PDFCategory, PDFSpecification
from ..types.differences import Difference
from ..types.comparison import (
    ComparisonResponse,
    ComparisonFeature,
    ComparisonSpecification,
    SpecificationValue,
    ComparisonSection
)
from .pdf_processor import PDFProcessor
from .transformers import UnitTransformer


class CompareProcessor(BaseModel):
    """Service for comparing PDF specifications.
    
    This class provides functionality for comparing multiple PDF specifications
    and identifying differences between them.
    
    Key capabilities:
    1. Compare features and advantages between products
    2. Analyze specification differences
    3. Generate structured comparison results
    4. Handle multiple product comparisons
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=True,
        extra="forbid",
        strict=True
    )

    pdf_processor: PDFProcessor = Field(default_factory=PDFProcessor)

    async def compare_models(self, model_numbers: List[str]) -> ComparisonResponse:
        """Compare specifications between multiple models.
        
        Args:
            model_numbers: List of model numbers to compare
            
        Returns:
            ComparisonResponse: Structured comparison data ready for API response
            
        Raises:
            Exception: If comparison fails
        """
        # Collect model data
        models = await self._collect_model_data(model_numbers)
        if not models:
            return ComparisonResponse(
                model_numbers=model_numbers,
                comparison_id=str(uuid.uuid4())
            )

        # Process features and advantages
        features = self._process_features(models, model_numbers)
        advantages = self._process_advantages(models, model_numbers)

        # Process specifications and differences
        sections, differences = self._process_specifications(models, model_numbers)

        # Create response with unified sections structure
        response_sections = {}
        
        # Add Features_And_Advantages section ONLY if there are actual features or advantages
        if features or advantages:
            categories = {}
            if features:
                categories["features"] = features
            if advantages:
                categories["advantages"] = advantages
            if categories:  # Only add if we have actual content
                response_sections["Features_And_Advantages"] = ComparisonSection(
                    categories=categories
                )
        
        # Add specification sections
        for section_name, specs in sections.items():
            # Group specifications by category
            categories: Dict[str, List[ComparisonSpecification]] = {}
            for spec in specs:
                if spec.category not in categories:
                    categories[spec.category] = []
                categories[spec.category].append(spec)
            
            response_sections[section_name] = ComparisonSection(
                categories=categories
            )

        # Calculate total differences count
        differences_count = len(differences)

        return ComparisonResponse(
            model_numbers=model_numbers,
            comparison_id=str(uuid.uuid4()),
            sections=response_sections,
            differences_count=differences_count
        )

    async def _collect_model_data(self, model_numbers: List[str]) -> Dict[str, PDFContent]:
        """Collect PDF data for each model."""
        models: Dict[str, PDFContent] = {}
        
        for model_num in model_numbers:
            try:
                result = self.pdf_processor.get_content(model_num)
                # Use model number from content if available, otherwise use input
                model_name = result.model_number or model_num
                models[model_name] = result
            except Exception as e:
                print(f"Warning: Failed to process model {model_num}: {e}")
                continue
            
        return models

    def _process_features(
        self,
        models: Dict[str, PDFContent],
        model_numbers: List[str]
    ) -> List[ComparisonFeature]:
        """Process features from all models."""
        return self._process_feature_type(models, model_numbers, "features")

    def _process_advantages(
        self,
        models: Dict[str, PDFContent],
        model_numbers: List[str]
    ) -> List[ComparisonFeature]:
        """Process advantages from all models."""
        return self._process_feature_type(models, model_numbers, "advantages")

    def _process_feature_type(
        self,
        models: Dict[str, PDFContent],
        model_numbers: List[str],
        feature_type: str
    ) -> List[ComparisonFeature]:
        """Process features or advantages from models."""
        features: List[ComparisonFeature] = []
        seen_texts = set()

        for model_name in model_numbers:
            if model_name not in models:
                continue

            model = models[model_name]
            if "Features_And_Advantages" not in model.sections:
                continue

            section = model.sections["Features_And_Advantages"]
            if feature_type not in section.categories:
                continue

            category = section.categories[feature_type]
            if "" not in category.subcategories:
                continue

            spec = category.subcategories[""]
            if not spec.value:
                continue

            # Split into lines and handle wrapped bullet points
            lines = [line.strip() for line in spec.value.split('\n') if line.strip()]
            processed_items = []
            current_item = ""

            for line in lines:
                if line.startswith('•') or line.startswith('-'):
                    if current_item:
                        processed_items.append(current_item)
                    current_item = line
                else:
                    if current_item:
                        current_item = f"{current_item} {line}"
                    else:
                        current_item = line

            if current_item:
                processed_items.append(current_item)

            # Create or update features
            for item in processed_items:
                if item in seen_texts:
                    # Update existing feature
                    for feature in features:
                        if feature.text == item:
                            feature.models[model_name] = True
                            break
                else:
                    # Create new feature
                    seen_texts.add(item)
                    models_dict = {name: name == model_name for name in model_numbers}
                    features.append(ComparisonFeature(
                        text=item,
                        models=models_dict
                    ))

        return features

    def _process_specifications(
        self,
        models: Dict[str, PDFContent],
        model_numbers: List[str]
    ) -> Tuple[Dict[str, List[ComparisonSpecification]], List[Difference]]:
        """Process specifications from all sections."""
        sections: Dict[str, List[ComparisonSpecification]] = {}
        differences: List[Difference] = []

        # First collect all unique section/category/specification combinations
        spec_combinations = []
        seen_combinations = set()

        # Process regular sections first
        for name in model_numbers:
            if name not in models:
                continue

            model = models[name]
            for section_name, section in model.sections.items():
                if section_name in ["Features_And_Advantages", "Diagram"]:
                    continue

                # Initialize section list if not exists
                if section_name not in sections:
                    sections[section_name] = []

                for category_name, category in section.categories.items():
                    for spec_name in category.subcategories.keys():
                        combination = (section_name, category_name, spec_name)
                        if combination not in seen_combinations:
                            spec_combinations.append(combination)
                            seen_combinations.add(combination)

        # Process each combination
        for section_name, category_name, spec_name in spec_combinations:
            values: Dict[str, SpecificationValue] = {}
            for name in model_numbers:
                if name in models:
                    spec = self._get_spec_value(
                        models[name],
                        section_name,
                        category_name,
                        spec_name
                    )
                    if spec:
                        values[name] = SpecificationValue(
                            value=spec.value,
                            unit=spec.unit,
                            display_value=spec.display_value
                        )

            if values:
                unique_values = {v.value for v in values.values()}
                has_differences = len(unique_values) > 1

                # Add specification to the section
                sections[section_name].append(ComparisonSpecification(
                    category=category_name,
                    specification=spec_name,
                    values=values,
                    has_differences=has_differences
                ))

                if has_differences:
                    # Get the model with the most different value
                    all_values = [float(v.value) if v.value.replace('.','',1).isdigit() else v.value for v in values.values()]
                    if all(isinstance(v, (int, float)) for v in all_values):
                        # For numeric values, find model with most extreme value
                        extreme_model = max(values.items(), key=lambda x: abs(float(x[1].value)))[0]
                        difference_desc = f"Value of {max(all_values)} vs {min(all_values)}"
                    else:
                        # For non-numeric values, take first model
                        extreme_model = next(iter(values.keys()))
                        other_values = [v.value for k, v in values.items() if k != extreme_model]
                        difference_desc = f"Value of {values[extreme_model].value} vs {', '.join(other_values)}"
                    
                    differences.append(Difference(
                        model=extreme_model,
                        category=section_name,
                        subcategory=category_name,
                        specification=spec_name,
                        difference=difference_desc,
                        unit=next(iter(values.values())).unit,
                        values={k: v.value for k, v in values.items()}
                    ))

        return sections, differences

    def _get_spec_value(
        self,
        model: PDFContent,
        section_name: str,
        category_name: str,
        spec_name: str
    ) -> Optional[PDFSpecification]:
        """Get specification value from model."""
        try:
            return model.get_specification(section_name, category_name, spec_name)
        except KeyError:
            return None 