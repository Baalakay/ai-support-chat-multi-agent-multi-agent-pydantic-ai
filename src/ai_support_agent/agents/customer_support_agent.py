"""CustomerSupportAgent implementation using PydanticAI v2 patterns."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict, computed_field, PrivateAttr
from pydantic_ai import Agent, RunContext, Tool

from ..types.agent import CustomerSupportDependencies
from ..types.product import QueryIntent, QueryDomain
from .product_specialist_agent import ProductSpecialistAgent
from ..config.config import get_settings
from ..types.base import BaseAgent


class CustomerResponse(BaseModel):
    """Response to a customer query."""
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "answer": "The HSR-520R operates at 24V DC",
                    "technical_details": {"voltage": "24V", "type": "DC"},
                    "confidence": 0.95
                }
            ]
        }
    )
    
    answer: str = Field(..., description="Clear answer to the query")
    technical_details: Dict[str, Any] = Field(..., description="Technical details supporting the answer")
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence in the response"
    )
    _raw_response: str = PrivateAttr(default="")
    
    @computed_field
    @property
    def has_technical_details(self) -> bool:
        """Check if response includes technical details."""
        return bool(self.technical_details)


class CustomerSupportAgent(BaseAgent[CustomerSupportDependencies]):
    """Agent for handling customer product queries."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        model=get_settings().default_model,
        temperature=get_settings().default_temperature,
        validate_assignment=True,
        frozen=True,
        extra="forbid"
    )
    
    _last_query: Dict[str, Any] = PrivateAttr(default_factory=dict)
    _query_history: List[Dict[str, Any]] = PrivateAttr(default_factory=list)
    
    def get_system_message(self) -> str:
        """Get the system message for the agent."""
        return """Customer support agent specializing in technical product inquiries. You excel at:
        1. Understanding customer queries about products
        2. Determining query domain and routing to specialists
        3. Determining specific aspects of interest
        4. Getting detailed product information from specialists
        5. Presenting information clearly and accurately
        6. Focusing on relevant details for customer needs
        7. Maintaining a helpful and professional tone
        8. Validating responses for accuracy
        9. Handling edge cases gracefully
        10. Extracting specific attributes when requested"""

    @Agent.tool
    async def handle_query(
        self,
        ctx: RunContext[CustomerSupportDependencies],
        query: str,
        model_numbers: List[str]
    ) -> CustomerResponse:
        """Handle a customer query about products.
        
        Args:
            ctx: Runtime context with dependencies
            query: The customer's question
            model_numbers: List of model numbers to analyze
            
        Returns:
            Formatted response with answer and supporting details
            
        Raises:
            ValueError: If query domain is not supported
        """
        try:
            # Store query in history
            self._last_query = {
                "query": query,
                "models": model_numbers,
                "timestamp": ctx.usage.current.get("timestamp")
            }
            self._query_history.append(self._last_query)
            
            # First determine query intent
            query_intent = await self.determine_intent(ctx, query)
            
            # Validate domain
            if query_intent.domain != QueryDomain.PRODUCT:
                raise ValueError(
                    f"Query domain '{query_intent.domain}' not supported by product specialist"
                )
            
            # Get product info from specialist
            product_info = await ctx.deps.product_specialist.analyze_products(
                ctx=ctx,
                model_numbers=model_numbers,
                query_intent=query_intent
            )
            
            # If specific attribute requested, extract it
            if query_intent.sub_topic and query_intent.sub_topic.lower() == "specific":
                attribute_path = self._get_attribute_path(query_intent)
                specific_info = await self.extract_specific_attribute(
                    ctx=ctx,
                    product_info=product_info,
                    attribute_path=attribute_path
                )
                if specific_info:
                    return CustomerResponse(
                        answer=str(specific_info["value"]),
                        confidence=specific_info["confidence"],
                        source_info=f"Extracted from {specific_info['path']}"
                    )
            
            # Create response based on query and product info
            prompt = self._create_response_prompt(
                query=query,
                query_intent=query_intent,
                product_info=product_info
            )
            
            response = await self.run(
                prompt=prompt,
                response_model=CustomerResponse,
                deps=ctx.deps
            )
            
            return response
            
        except Exception as e:
            raise

    @Agent.tool
    async def determine_intent(
        self,
        ctx: RunContext[CustomerSupportDependencies],
        query: str
    ) -> QueryIntent:
        """Determine the intent and focus of the query.
        
        Args:
            ctx: Runtime context with dependencies
            query: The customer's question
            
        Returns:
            Structured understanding of query intent
        """
        prompt = f"""Analyze this product query to determine the specific focus:

Query: {query}

Determine:
1. Query domain (product, case_study, company, careers)
2. Main topic (e.g., specifications, operation, performance)
3. Specific aspect or attribute of interest
4. Any constraints or filters to apply
5. Whether comparison is needed (if multiple models)

Provide a structured analysis of what information is needed.
The domain MUST be one of: product, case_study, company, careers."""

        response = await self.run(
            prompt=prompt,
            response_model=QueryIntent,
            deps=ctx.deps
        )
        
        return response

    def _create_response_prompt(
        self,
        query: str,
        query_intent: QueryIntent,
        product_info: Dict[str, Any]
    ) -> str:
        """Create prompt for generating customer response."""
        prompt_parts = [
            f"Customer Query: {query}\n",
            f"Query Domain: {query_intent.domain}",
            f"Query Focus: {query_intent.topic} - {query_intent.sub_topic}\n",
            "Product Information:"
        ]
        
        # Add specs
        if "specifications" in product_info:
            prompt_parts.append("\nSpecifications:")
            prompt_parts.append(str(product_info["specifications"]))
        
        # Add differences if present
        if product_info.get("differences"):
            prompt_parts.append("\nKey Differences:")
            prompt_parts.append(str(product_info["differences"]))
        
        # Add AI findings if present
        if product_info.get("ai_findings"):
            prompt_parts.append("\nAnalysis:")
            prompt_parts.append(str(product_info["ai_findings"]))
        
        prompt_parts.extend([
            "\nProvide:",
            "1. Clear answer addressing the specific query focus",
            "2. Relevant technical details to support the answer",
            "3. Confidence level in the response"
        ])
        
        return "\n".join(prompt_parts)
    
    @computed_field
    @property
    def last_query_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the last query."""
        return self._last_query if self._last_query else None
    
    @computed_field
    @property
    def query_count(self) -> int:
        """Get total number of queries handled."""
        return len(self._query_history)

    @Agent.tool
    async def extract_specific_attribute(
        self,
        ctx: RunContext[CustomerSupportDependencies],
        product_info: Dict[str, Any],
        attribute_path: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Extract a specific attribute from product information.
        
        Args:
            ctx: Runtime context with dependencies
            product_info: Full product information from PSA
            attribute_path: Path to desired attribute (e.g. ["specifications", "Electrical", "Voltage"])
            
        Returns:
            Extracted attribute value if found, None otherwise
        """
        try:
            # Navigate through the attribute path
            current = product_info
            for key in attribute_path:
                if isinstance(current, dict):
                    current = current.get(key)
                else:
                    return None
                
            # Return formatted result
            return {
                "value": current,
                "path": ".".join(attribute_path),
                "confidence": 1.0 if current is not None else 0.0
            }
            
        except Exception as e:
            return None

    def _get_attribute_path(self, query_intent: QueryIntent) -> List[str]:
        """Get attribute path from query intent context."""
        path = []
        
        # Add base path component
        if "section" in query_intent.context:
            path.append(query_intent.context["section"])
        
        # Add category if present
        if "category" in query_intent.context:
            path.append(query_intent.context["category"])
        
        # Add specification if present
        if "specification" in query_intent.context:
            path.append(query_intent.context["specification"])
        
        return path 