"""Types for PDF processing and content.

Type Hierarchy:
PDFContent
├── raw_text: str
├── model_number: Optional[str]
├── pages: List[PDFPage]
│   └── PDFPage
│       ├── number: int
│       ├── text: str
│       └── tables: List[List[List[str]]]
└── sections: Dict[str, PDFSection]
    └── PDFSection
        └── categories: Dict[str, PDFCategory]
            └── PDFCategory
                └── subcategories: Dict[str, PDFSpecification]
                    └── PDFSpecification
                        ├── value: str
                        ├── unit: Optional[str]
                        └── display_value: str
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, computed_field

from ..tools.transformers import UnitTransformer


class PDFSpecification(BaseModel):
    """Individual specification with unit and value."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True
    )
    
    unit: Optional[str] = Field(None, description="Unit of measurement if applicable")
    value: str = Field(..., description="Specification value")

    @computed_field
    def display_value(self) -> str:
        """Get the formatted display value using the transformer."""
        return UnitTransformer.format_display_value(self.value, self.unit)


class PDFCategory(BaseModel):
    """Category containing subcategories of specifications."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True
    )
    
    subcategories: Dict[str, PDFSpecification] = Field(
        default_factory=dict,
        description="Map of subcategory names to specifications"
    )


class PDFSection(BaseModel):
    """Section containing categories of specifications."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True
    )
    
    categories: Dict[str, PDFCategory] = Field(
        default_factory=dict,
        description="Map of category names to categories"
    )


class PDFPage(BaseModel):
    """Individual page from a PDF."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True
    )
    
    number: int = Field(..., description="Page number")
    text: str = Field(..., description="Raw text content")
    tables: List[List[List[str]]] = Field(
        default_factory=list,
        description="Tables extracted from the page"
    )


class PDFContent(BaseModel):
    """Complete content extracted from a PDF."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True
    )
    
    raw_text: str = Field(..., description="Raw text content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the PDF"
    )
    pages: List[PDFPage] = Field(
        default_factory=list,
        description="List of pages in the PDF"
    )
    model_number: Optional[str] = Field(
        None,
        description="Model number if found in the PDF"
    )
    sections: Dict[str, PDFSection] = Field(
        default_factory=dict,
        description="Map of section names to sections"
    )

    def get_specification(
        self,
        section: str,
        category: str,
        subcategory: str = ""
    ) -> Optional[PDFSpecification]:
        """Get a specific specification value.
        
        Args:
            section: Section name
            category: Category name
            subcategory: Subcategory name (empty string for no subcategory)
            
        Returns:
            Specification if found, None otherwise
        """
        try:
            return (
                self.sections[section]
                .categories[category]
                .subcategories[subcategory]
            )
        except KeyError:
            return None


class PDFProcessingError(Exception):
    """Base class for PDF processing errors."""
    pass


class PDFExtractionError(PDFProcessingError):
    """Error extracting content from PDF."""
    pass


class PDFValidationError(PDFProcessingError):
    """Error validating PDF content."""
    pass 