"""Service for comparing PDF specifications."""
from typing import Dict, List, Optional, Any
import uuid
from pathlib import Path
import pandas as pd
import hashlib

from ai_support_agent.types.pdf import PDFContent, PDFSection, PDFCategory, PDFSpecification, PDFPage
from ai_support_agent.tools.pdf_processor import PDFProcessor
from ai_support_agent.types.differences import Difference
from ai_support_agent.types.comparison import (
    ComparisonResponse,
    ComparisonFeature,
    ComparisonSpecification,
    SpecificationValue
)
from .transformers import UnitTransformer


class PDFComparison:
    """Service for comparing PDFs."""

    def __init__(self) -> None:
        """Initialize the comparison processor."""
        self.pdf_processor = PDFProcessor()

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
        specifications, differences = self._process_specifications(models, model_numbers)

        # Create response
        return ComparisonResponse(
            model_numbers=model_numbers,
            comparison_id=str(uuid.uuid4()),
            features=features,
            advantages=advantages,
            specifications=specifications,
            differences_count=len(differences),
            metadata={
                "source": "pdf_processor",
                "version": "1.0.0"
            }
        )

    async def _collect_model_data(self, model_numbers: List[str]) -> Dict[str, PDFContent]:
        """Collect PDF data for each model."""
        models: Dict[str, PDFContent] = {}
        
        print(f"\nCollecting data for models: {model_numbers}")
        for model_num in model_numbers:
            try:
                print(f"\nProcessing model: {model_num}")
                result = self.pdf_processor.get_content(model_num)
                # Use model number from content if available, otherwise use input
                model_name = result.model_number or model_num
                print(f"Got content for {model_name}")
                print(f"Sections: {list(result.sections.keys())}")
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
    ) -> tuple[List[ComparisonSpecification], List[Difference]]:
        """Process specifications from all sections."""
        specifications: List[ComparisonSpecification] = []
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
                        # Use the existing display_value and unit from PDFSpecification
                        values[name] = SpecificationValue(
                            value=spec.value,
                            unit=spec.unit,
                            display_value=spec.display_value
                        )

            if values:
                unique_values = {v.value for v in values.values()}
                has_differences = len(unique_values) > 1

                spec = ComparisonSpecification(
                    section=section_name,
                    category=category_name,
                    specification=spec_name,
                    values=values,
                    has_differences=has_differences
                )
                specifications.append(spec)

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

        # Process diagram section last
        has_diagrams = False
        diagram_values: Dict[str, SpecificationValue] = {}
        
        # First check which models have diagrams and collect their paths
        for model_name in model_numbers:
            if model_name in models and "Diagram" in models[model_name].sections:
                has_diagrams = True
                model = models[model_name]
                section = model.sections["Diagram"]
                if "" in section.categories:
                    category = section.categories[""]
                    if "" in category.subcategories:
                        spec = category.subcategories[""]
                        if spec.value:
                            # Use existing display_value for diagrams too
                            diagram_values[model_name] = SpecificationValue(
                                value=spec.value,
                                unit=spec.unit,
                                display_value=spec.display_value
                            )

        # If any model has a diagram, create a specification for all models
        if has_diagrams:
            # Create diagram specification with empty category/specification to match processor
            spec = ComparisonSpecification(
                section="Diagram",
                category="",
                specification="",
                values=diagram_values,
                has_differences=len(set(v.value for v in diagram_values.values())) > 1
            )
            specifications.append(spec)

        return specifications, differences

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

    def _extract_model_name(self, pdf_name: str) -> str:
        """Extract model name from PDF file name."""
        # This is a placeholder implementation. You might want to implement a more robust model name extraction logic based on your file naming convention or by reading the PDF file metadata.
        return pdf_name.split('_')[0]  # Simple example: split by underscore and take the first part

    def _create_pdf_content(self, pdf_path: Path, text: str, tables: List[List[str]]) -> PDFContent:
        """Create a PDFContent object from a PDF file."""
        # This is a placeholder implementation. You might want to implement a more robust PDFContent creation logic based on your PDF file reading and processing logic.
        # For example, you can use a PDF processing library to extract text, tables, and other metadata from the PDF file.
        sections = {
            "Features_And_Advantages": PDFSection(
                categories={
                    "features": PDFCategory(
                        subcategories={
                            "": PDFSpecification(value="Features:")
                        }
                    ),
                    "advantages": PDFCategory(
                        subcategories={
                            "": PDFSpecification(value="Advantages:")
                        }
                    )
                }
            )
        }

        # Extract model name
        model_name = self._extract_model_name(pdf_path.name)

        # Calculate file hash
        file_hash = hashlib.sha256(str(pdf_path).encode()).hexdigest()

        # Create PDFContent
        return PDFContent(
            raw_text=text,
            metadata={},
            pages=[PDFPage(
                number=1,
                text=text,
                tables=tables
            )],
            model_number=model_name,
            sections=sections
        ) 
