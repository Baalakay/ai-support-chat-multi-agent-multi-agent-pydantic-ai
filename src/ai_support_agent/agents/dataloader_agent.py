"""DataLoader Agent for processing PDF content."""
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, RunContext
from datetime import datetime, UTC

from ..types.agent import DataLoaderDependencies
from ..types.pdf import PDFContent, PDFProcessingError
from ..config.config import get_settings


class LoadResult(BaseModel):
    """Result of loading PDF files."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid"
    )
    
    processed_files: List[str] = Field(..., description="List of successfully processed files")
    failed_files: List[str] = Field(default_factory=list, description="List of files that failed to process")
    error_messages: Dict[str, str] = Field(default_factory=dict, description="Error messages for failed files")


class DataLoaderAgent(Agent[DataLoaderDependencies]):
    """Agent for loading and managing product data."""
    
    def get_system_message(self) -> str:
        """Get the system message for the agent."""
        return """Data loading specialist focused on:
        1. Loading and processing product data from PDFs
        2. Validating data formats and content
        3. Extracting structured information"""

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Validate required paths exist during class initialization."""
        super().__init_subclass__(**kwargs)
        settings = get_settings()
        if not settings.pdf_dir.exists():
            raise ValueError(f"PDF directory does not exist: {settings.pdf_dir}")

    @Agent.tool
    async def get_product_data(self, ctx: RunContext[DataLoaderDependencies], *, model_number: str) -> PDFContent:
        """Get product data by processing the PDF file.
        
        Args:
            ctx: Runtime context with dependencies
            model_number: Model number to retrieve
            
        Returns:
            Product data content
            
        Raises:
            PDFProcessingError: If processing fails
            ValueError: If model number is invalid
        """
        try:
            # Validate model number
            if not await self.validate_model_number(ctx, model_number=model_number):
                raise ValueError(f"Invalid model number format: {model_number}")
            
            # Get PDF path for model
            settings = get_settings()
            pdf_path = settings.pdf_dir / f"{model_number}.pdf"
            
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF not found for model: {model_number}")
            
            # Process PDF directly
            content = ctx.deps.pdf_processor.get_content(str(pdf_path))
            return content
            
        except Exception as e:
            raise

    @Agent.tool
    async def process_file(self, ctx: RunContext[DataLoaderDependencies], *, file_path: str) -> PDFContent:
        """Process a PDF file.
        
        Args:
            ctx: Runtime context with dependencies
            file_path: Path to the PDF file
            
        Returns:
            Processed PDF content
            
        Raises:
            PDFProcessingError: If processing fails
        """
        try:
            # Process PDF
            content = ctx.deps.pdf_processor.get_content(file_path)
            return content
            
        except Exception as e:
            raise

    @Agent.tool
    async def validate_model_number(self, ctx: RunContext[DataLoaderDependencies], *, model_number: str) -> bool:
        """Validate a model number format.
        
        Args:
            ctx: Runtime context with dependencies
            model_number: Model number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not model_number:
            return False
            
        # Check if PDF exists for model
        settings = get_settings()
        pdf_path = settings.pdf_dir / f"{model_number}.pdf"
        return pdf_path.exists()

    @Agent.tool
    async def process_directory(
        self,
        ctx: RunContext[DataLoaderDependencies],
        *,
        directory: Path | str
    ) -> LoadResult:
        """Process all PDF files in a directory.
        
        Args:
            ctx: Runtime context with dependencies
            directory: Directory containing PDF files
            
        Returns:
            LoadResult with processing results
        """
        directory = Path(directory)
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
            
        processed = []
        failed = []
        errors = {}
        
        for pdf_file in directory.glob("*.pdf"):
            try:
                await self.process_file(ctx, file_path=str(pdf_file))
                processed.append(pdf_file.name)
            except Exception as e:
                failed.append(pdf_file.name)
                errors[pdf_file.name] = str(e)
                
        return LoadResult(
            processed_files=processed,
            failed_files=failed,
            error_messages=errors
        )

    @Agent.tool_plain
    def validate_pdf_path(self, file_path: str) -> bool:
        """Validate a PDF file path.
        
        Args:
            file_path: Path to validate
            
        Returns:
            True if valid PDF path, False otherwise
        """
        path = Path(file_path)
        return path.exists() and path.suffix.lower() == ".pdf" 