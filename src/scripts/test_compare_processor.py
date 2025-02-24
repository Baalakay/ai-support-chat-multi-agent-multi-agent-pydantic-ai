#!/usr/bin/env python3
"""Test script for the CompareProcessor."""

import asyncio
import json
from pathlib import Path
import sys

# Add src to Python path
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from ai_support_agent.tools.compare_processor import CompareProcessor


async def main():
    """Run comparison test."""
    # Initialize processor
    processor = CompareProcessor()
    
    # Models to compare
    models = ["520R", "980F"]
    
    # Run comparison
    try:
        result = await processor.compare_models(models)
        
        # Convert to dict for JSON serialization
        result_dict = result.model_dump()
        
        # Print results
        print(json.dumps(result_dict, indent=2))
        
    except Exception as e:
        print(f"Error during comparison: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 