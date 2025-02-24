#!/usr/bin/env python3
"""Test script for the ProductSpecialistAgent with real processes."""

import asyncio
import json
from pathlib import Path
import sys
import argparse
from typing import Dict, Any, List, Optional

# Add src to Python path
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from ai_support_agent.agents.product_specialist_agent import ProductSpecialistAgent
from ai_support_agent.types.product import QueryIntent, QueryDomain, DisplayPreferences
from ai_support_agent.types.agent import AgentDependencies
from ai_support_agent.config.config import get_settings
from pydantic_ai import RunContext
from pydantic_ai.usage import Usage


# Available models for testing
AVAILABLE_MODELS = ["520R", "980F", "112F"]


def create_agent_context(sections: Optional[List[str]] = None) -> tuple[ProductSpecialistAgent, RunContext]:
    """Create agent and context with specified settings."""
    agent = ProductSpecialistAgent()
    settings = get_settings()
    
    # Create usage tracker
    usage_tracker = Usage()
    
    # Create display preferences as a dict
    display_prefs = {
        "output_format": "text",
        "sections_to_show": sections or ["all"],
        "show_differences_only": False,
        "include_metadata": True
    }
    
    # Create dependencies without storage service
    deps = AgentDependencies(
        usage_tracker=usage_tracker,
        model_name=settings.default_model,
        temperature=settings.default_temperature,
        display_preferences=display_prefs
    )
    
    return agent, RunContext(deps=deps)


def normalize_section_name(section: str) -> str:
    """Convert user-friendly section name to internal representation."""
    # Map of user-friendly names to internal names
    section_map = {
        "electrical specifications": "electrical",
        "magnetic specifications": "magnetic",
        "physical specifications": "physical",
        "features and advantages": "Features_And_Advantages",
        "features": "Features_And_Advantages",
        "advantages": "Features_And_Advantages",
        "diagram": "diagram"
    }
    
    # First try exact match
    normalized = section_map.get(section.lower())
    if normalized:
        return normalized
        
    # Then try prefix match
    for user_name, internal_name in section_map.items():
        if section.lower().startswith(user_name.split()[0]):
            return internal_name
            
    # If no match found, return as is (will be validated later)
    return section


async def test_single_model(model_number: str, section: str = "electrical"):
    """Test single model analysis with real PDF processing."""
    print(f"\nTesting Single Model Analysis for {model_number}...")
    
    # Initialize agent and context
    agent, ctx = create_agent_context([section])
    
    # Query for specified section
    query_intent = QueryIntent(
        domain=QueryDomain.PRODUCT,
        topic="specifications",
        sub_topic=section,
        context={"section": section}
    )
    
    try:
        result = await agent.analyze_products(
            ctx=ctx,
            model_numbers=[model_number],
            query_intent=query_intent
        )
        
        # Print results
        print("\nAnalysis Results:")
        print(json.dumps(result.model_dump(), indent=2))
        
        # Verify sections
        if result.specifications:
            print("\nFound sections:")
            for section in result.specifications.keys():
                print(f"- {section}")
        
    except Exception as e:
        print(f"Error analyzing model: {e}")
        raise


async def test_model_comparison(models: List[str], sections: Optional[List[str]] = None):
    """Test model comparison with real processors."""
    print(f"\nTesting Model Comparison for models: {models}")
    
    # Initialize agent and context
    agent, ctx = create_agent_context(sections)
    
    # Comparison query
    query_intent = QueryIntent(
        domain=QueryDomain.PRODUCT,
        topic="comparison",
        sub_topic="all",
        context={"compare": "full"}
    )
    
    try:
        result = await agent.analyze_products(
            ctx=ctx,
            model_numbers=models,
            query_intent=query_intent
        )
        
        # Print comparison results
        print("\nComparison Results:")
        print(json.dumps(result.model_dump(), indent=2))
        
        # Print differences summary
        if result.differences:
            print(f"\nFound {len(result.differences)} differences:")
            for diff in result.differences:
                print(f"\nCategory: {diff.category}")
                print(f"Specification: {diff.specification}")
                print("Values:")
                for model, value in diff.values.items():
                    print(f"  {model}: {value}")
                if diff.unit:
                    print(f"Unit: {diff.unit}")
        
        # Print AI findings if available
        if result.ai_findings:
            print("\nAI Analysis:")
            print(json.dumps(result.ai_findings, indent=2))
        
    except Exception as e:
        print(f"Error comparing models: {e}")
        raise


async def test_features_and_advantages(model_number: str):
    """Test features and advantages analysis."""
    print(f"\nTesting Features and Advantages Analysis for {model_number}...")
    
    # Initialize agent and context
    agent, ctx = create_agent_context(["Features_And_Advantages"])
    
    # Features query
    query_intent = QueryIntent(
        domain=QueryDomain.PRODUCT,
        topic="features",
        sub_topic="all",
        context={"section": "Features_And_Advantages"}
    )
    
    try:
        result = await agent.analyze_products(
            ctx=ctx,
            model_numbers=[model_number],
            query_intent=query_intent
        )
        
        # Print results
        print("\nFeatures Analysis:")
        print(json.dumps(result.model_dump(), indent=2))
        
        # Print features if found
        if result.specifications and "Features_And_Advantages" in result.specifications:
            features = result.specifications["Features_And_Advantages"]
            print("\nFeatures found:")
            print(json.dumps(features, indent=2))
        
    except Exception as e:
        print(f"Error analyzing features: {e}")
        raise


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test ProductSpecialistAgent with different configurations")
    
    parser.add_argument(
        "--mode",
        choices=["single", "comparison", "features", "all"],
        default="all",
        help="Test mode to run"
    )
    
    parser.add_argument(
        "--models",
        nargs="+",
        choices=AVAILABLE_MODELS,
        default=["520R"],
        help="Models to test (1-3 models)"
    )
    
    parser.add_argument(
        "--sections",
        nargs="+",
        default=["electrical specifications", "magnetic specifications"],
        help="Sections to analyze (e.g. 'electrical specifications', 'magnetic specifications')"
    )
    
    args = parser.parse_args()
    
    # Validate number of models
    if len(args.models) > 3:
        parser.error("Maximum 3 models allowed")
    
    # Normalize section names
    args.sections = [normalize_section_name(s) for s in args.sections]
    
    return args


async def main():
    """Run tests based on command line arguments."""
    args = parse_args()
    print("Starting ProductSpecialistAgent Integration Tests...")
    print(f"Mode: {args.mode}")
    print(f"Models: {args.models}")
    print(f"Sections: {args.sections}")
    
    try:
        if args.mode in ["single", "all"]:
            await test_single_model(args.models[0], args.sections[0])
        
        if args.mode in ["comparison", "all"] and len(args.models) > 1:
            await test_model_comparison(args.models, args.sections)
        
        if args.mode in ["features", "all"]:
            await test_features_and_advantages(args.models[0])
        
        print("\nAll requested tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest suite failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 