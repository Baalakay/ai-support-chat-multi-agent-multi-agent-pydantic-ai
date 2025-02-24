"""Tool for managing and formatting prompts."""

from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from pydantic_ai import Agent, RunContext

from ..types.agent import AgentDependencies
from ..config.config import get_settings


class PromptManager(Agent[AgentDependencies]):
    """Tool for managing and formatting prompts."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid"
    )
    
    templates: Dict[str, str] = Field(
        default_factory=dict,
        description="Loaded prompt templates"
    )
    template_dir: Path = Field(
        default=Path("src/ai_support_agent/tools/prompts"),
        description="Directory containing prompt templates"
    )
    
    def __init__(self, **data: Any):
        """Initialize and load templates."""
        super().__init__(**data)
        try:
            settings = get_settings()
            self.template_dir = settings.template_dir
        except Exception as e:
            self.template_dir = Path(__file__).parent / "prompts"
        self.load_templates()
    
    def get_system_message(self) -> str:
        """Get the system message for the agent."""
        return """Prompt management specialist focused on:
        1. Loading and validating prompt templates
        2. Formatting prompts with variables
        3. Maintaining template consistency
        4. Providing template information"""
    
    @Agent.tool
    async def get_prompt(
        self,
        ctx: RunContext[AgentDependencies],
        template_name: str,
        variables: Dict[str, Any]
    ) -> str:
        """Get a formatted prompt.
        
        Args:
            ctx: Runtime context with dependencies
            template_name: Name of the template to use
            variables: Variables to format the template with
            
        Returns:
            Formatted prompt
            
        Raises:
            KeyError: If template not found
        """
        if template_name not in self.templates:
            raise KeyError(f"Template not found: {template_name}")
            
        template = self.templates[template_name]
        try:
            return template.format(**variables)
        except KeyError as e:
            raise KeyError(f"Missing variable in template: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to format template: {str(e)}")
    
    @Agent.tool
    async def validate_template(
        self,
        ctx: RunContext[AgentDependencies],
        template_name: str,
        test_variables: Dict[str, Any]
    ) -> bool:
        """Validate that a template can be formatted with given variables."""
        try:
            await self.get_prompt(ctx, template_name, test_variables)
            return True
        except Exception as e:
            return False 