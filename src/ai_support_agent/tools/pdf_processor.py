"""Service for processing PDF specifications."""

from typing import Dict, List, Optional, Any
from pathlib import Path
import pdfplumber
import fitz  # type: ignore  # PyMuPDF
import re
from pydantic import BaseModel, Field, ConfigDict, PrivateAttr

from ..config.config import get_settings
from ..types.pdf import (
    PDFContent,
    PDFPage,
    PDFSection,
    PDFCategory,
    PDFSpecification,
    PDFProcessingError,
    PDFExtractionError,
    PDFValidationError
)
from .transformers import UnitTransformer


class PDFProcessor(BaseModel):
    """Service for processing PDF specifications.
    
    This class provides PDF processing functionality for extracting and structuring
    content from PDF files containing product specifications.
    
    Key capabilities:
    1. Extract text and tables from PDFs
    2. Parse features and advantages sections
    3. Process specification tables
    4. Extract and save diagrams
    5. Validate extracted content
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=True,
        extra="forbid",
        strict=True
    )
    
    pdf_dir: Path = Field(default_factory=lambda: get_settings().pdf_dir)
    diagram_dir: Path = Field(default_factory=lambda: get_settings().diagram_dir)
    text_sections: List[str] = Field(default=["features", "advantages", "notes"])
    section_patterns: Dict[str, str] = Field(default={
        'electrical': 'electrical specifications',
        'magnetic': 'magnetic specifications',
        'physical': 'physical/operational specifications'
    })
    section_order: List[str] = Field(default=["electrical", "magnetic", "physical"])
    _current_file: Optional[Path] = PrivateAttr(default=None)

    def get_content(self, model_or_path: str | Path) -> PDFContent:
        """Get PDF content from model number or file path.
        
        Args:
            model_or_path: Model number or file path
            
        Returns:
            Processed PDF content
            
        Raises:
            PDFProcessingError: If processing fails
        """
        try:
            # Convert to Path if string
            path = Path(model_or_path)
            
            # If not in pdf_dir, check if it's a model number and try to find the file
            if not path.exists() and not path.is_absolute():
                for pdf_file in self.pdf_dir.glob("*.pdf"):
                    if path.stem.upper() in pdf_file.stem.upper():
                        path = pdf_file
                        break
                if not path.exists():
                    raise PDFProcessingError(f"No PDF found for {model_or_path} in {self.pdf_dir}")
            
            # Validate file
            if not path.exists() or path.suffix.lower() != '.pdf':
                raise PDFProcessingError(f"Invalid PDF path: {path}")
            
            self._current_file = path
            
            # Extract content
            content = self._extract_content(path)
            
            # Validate content
            try:
                content.model_validate(content)
            except Exception as e:
                raise PDFValidationError(f"Content validation failed: {str(e)}")
            
            return content
            
        except Exception as e:
            raise PDFProcessingError(f"Failed to process PDF: {str(e)}")

    def _extract_content(self, path: Path) -> PDFContent:
        """Extract content from PDF file."""
        try:
            # Get raw text
            text = self._extract_text(str(path))
            
            # Extract model number from filename
            model_name = self._extract_model_name(path.name)
            
            # Extract tables
            tables = self._extract_tables(text)
            
            # Create pages
            pages = [PDFPage(number=1, text=text, tables=tables)]
            
            # Process features and advantages
            sections = self._parse_features_advantages(text, tables) or {}
            
            # Process specification tables
            spec_sections = self._process_specification_tables(text, tables)
            sections.update(spec_sections)
            
            # Extract and save diagram
            if model_name:
                # Ensure diagram directory exists
                self.diagram_dir.mkdir(parents=True, exist_ok=True)
                
                # Extract diagram using PyMuPDF
                diagram_path = self.diagram_dir / f"{model_name}.png"
                if not diagram_path.exists():
                    try:
                        doc = fitz.open(str(path))
                        page = doc[0]  # First page
                        
                        # Get the diagram area (top-right corner)
                        rect = fitz.Rect(300, 0, 600, 120)
                        
                        # Extract image
                        pix = page.get_pixmap(clip=rect)
                        pix.save(str(diagram_path))
                        doc.close()
                    except Exception as e:
                        pass  # Diagram extraction is optional
                
                # Add diagram section if image exists
                if diagram_path.exists():
                    sections["Diagram"] = PDFSection(
                        categories={
                            "": PDFCategory(
                                subcategories={
                                    "": PDFSpecification(
                                        value=str(diagram_path),
                                        unit=None
                                    )
                                }
                            )
                        }
                    )
            
            return PDFContent(
                raw_text=text,
                model_number=model_name,
                pages=pages,
                sections=sections
            )
            
        except Exception as e:
            raise PDFExtractionError(f"Failed to extract content: {str(e)}")

    def _extract_text(self, filename: str) -> str:
        """Extract text from the first page of a PDF file."""
        path = Path(filename)
        self._current_file = path
        with pdfplumber.open(path) as pdf:
            first_page = pdf.pages[0]
            return first_page.extract_text()

    def _extract_tables(self, text: str) -> List[List[List[str]]]:
        """Extract tables from PDF."""
        if not self._current_file:
            return []
        with pdfplumber.open(self._current_file) as pdf:
            first_page = pdf.pages[0]
            tables = first_page.extract_tables()
            # Convert None values to empty strings
            return [
                [[str(cell) if cell else '' for cell in row] for row in table]
                for table in tables
            ]

    def _parse_features_advantages(
        self,
        text: str,
        tables: List[List[List[str]]]
    ) -> Optional[Dict[str, PDFSection]]:
        """Extract features and advantages using bounding boxes."""
        if not self._current_file:
            return None

        features: List[str] = []
        advantages: List[str] = []

        with pdfplumber.open(self._current_file) as pdf:
            page = pdf.pages[0]

            # Extract features from left box
            feat_box = (0, 130, 295, 210)
            feat_area = page.within_bbox(feat_box)
            feat_text = feat_area.extract_text()
            if feat_text:
                features = []
                for line in feat_text.split('\n'):
                    line = line.strip()
                    if line and line.lower() != 'features':
                        features.append(line)

            # Extract advantages from right box
            adv_box = (300, 130, 610, 210)
            adv_area = page.within_bbox(adv_box)
            adv_text = adv_area.extract_text()
            if adv_text:
                advantages = []
                for line in adv_text.split('\n'):
                    line = line.strip()
                    if line and line.lower() != 'advantages':
                        advantages.append(line)

        if features or advantages:
            return {
                'Features_And_Advantages': PDFSection(
                    categories={
                        'features': PDFCategory(
                            subcategories={
                                '': PDFSpecification(
                                    value='\n'.join(features)
                                )
                            }
                        ),
                        'advantages': PDFCategory(
                            subcategories={
                                '': PDFSpecification(
                                    value='\n'.join(advantages)
                                )
                            }
                        )
                    }
                )
            }
        return None

    def _process_specification_tables(
        self,
        text: str,
        tables: List[List[List[str]]]
    ) -> Dict[str, PDFSection]:
        """Process specification tables into sections."""
        sections: Dict[str, PDFSection] = {}
        
        for table in tables:
            specs = self._parse_table_to_specs(table)
            if specs:
                for section_name, categories in specs.items():
                    if section_name not in sections:
                        sections[section_name] = PDFSection(categories={})
                    for category_name, subcategories in categories.items():
                        sections[section_name].categories[category_name] = PDFCategory(
                            subcategories=subcategories
                        )
        
        return sections

    def _parse_table_to_specs(
        self,
        table: List[List[str]]
    ) -> Dict[str, Dict[str, Dict[str, PDFSpecification]]]:
        """Parse a table into specifications."""
        if not table:  # Empty table
            return {}

        # Clean first row
        first_row = [
            str(col).strip() if col else "" for col in table[0]
        ]

        # Skip features/advantages table
        if (len(first_row) == 2 and
                "Features" in first_row[0] and
                "Advantages" in first_row[1]):
            return {}

        specs: Dict[str, Dict[str, Dict[str, PDFSpecification]]] = {}
        current_category: Optional[str] = None
        current_section: Optional[str] = None

        # Check if first row is data
        is_first_row_data = (
            len(first_row) >= 3 and  # At least category, unit, value columns
            first_row[0] and  # Must have a category
            any(first_row[-2:])  # Must have either unit or value
        )

        # Process rows
        rows_to_process = table if is_first_row_data else table[1:]

        # Helper function to determine section for a category
        def get_section_for_category(category: str) -> str:
            # Map specific categories to their sections
            category_lower = category.lower()
            
            # Electrical section categories
            if any(term in category_lower for term in [
                'power', 'voltage', 'current', 'resistance', 'capacitance', 
                'temperature', 'electrical'
            ]):
                return self.section_patterns['electrical']
            
            # Magnetic section categories
            elif any(term in category_lower for term in [
                'pull - in', 'test coil', 'magnetic'
            ]):
                return self.section_patterns['magnetic']
            
            # Physical section categories
            elif any(term in category_lower for term in [
                'capsule', 'contact material', 'operate time', 'release time',
                'physical', 'operational'
            ]):
                return self.section_patterns['physical']
            
            # If no match found, use current section or first section as default
            return current_section or self.section_patterns[self.section_order[0]]

        for row in rows_to_process:
            try:
                # Clean row data
                row_data = [
                    str(cell).strip() if cell else "" for cell in row
                ]

                if not any(row_data):  # Skip empty rows
                    continue

                # Get category and subcategory
                category = row_data[0] if row_data[0] else current_category
                subcategory = (
                    row_data[1] if len(row_data) > 1 and row_data[1] else ""
                )

                # Handle empty first column
                if not category and subcategory:
                    category = current_category

                if category and isinstance(category, str):
                    current_category = category
                    # Determine the correct section for this category
                    section_name = get_section_for_category(category)
                    current_section = section_name
                    if section_name not in specs:
                        specs[section_name] = {}
                    if category not in specs[section_name]:
                        specs[section_name][category] = {}

                # Get unit and value - unit in column 3, value in column 4
                if len(row_data) > 3:  # Need at least 4 columns for value
                    # Unit is in column 3, value in column 4
                    raw_unit = row_data[2].strip() if row_data[2] else None
                    value = row_data[3].strip()

                    if category and current_section:
                        # Initialize empty subcategories dict if needed
                        if category not in specs[current_section]:
                            specs[current_section][category] = {}
                        
                        # Standardize unit using transformer
                        unit = UnitTransformer.standardize_unit(raw_unit)
                        
                        # Create specification with standardized unit and value
                        spec = PDFSpecification(unit=unit, value=value)
                        
                        # Add to structure with proper nesting
                        if subcategory:
                            if subcategory not in specs[current_section][category]:
                                specs[current_section][category][subcategory] = {}
                            specs[current_section][category][subcategory] = spec
                        else:
                            specs[current_section][category][""] = spec

            except (ValueError, IndexError):
                continue

        return specs

    def _extract_model_name(self, filename: str) -> Optional[str]:
        """Extract model number from filename."""
        # Remove extension and split on underscores/spaces
        base_name = Path(filename).stem
        
        # First try to find HSR-\d+ pattern
        hsr_match = re.search(r'HSR-?(\d+[RFW]?)', base_name, re.IGNORECASE)
        if hsr_match:
            return hsr_match.group(1).upper()
        
        # Then try just the number with optional suffix
        parts = re.split(r'[_\s]', base_name)
        for part in parts:
            # Basic pattern: digits followed by optional R/F/W
            if re.match(r'^\d+[RFW]?$', part, re.IGNORECASE):
                return part.upper()
        
        # If no match found and input is just digits, use that
        if base_name.isdigit():
            return base_name
        
        return None

# Rebuild model to ensure all types are properly resolved
PDFProcessor.model_rebuild()

