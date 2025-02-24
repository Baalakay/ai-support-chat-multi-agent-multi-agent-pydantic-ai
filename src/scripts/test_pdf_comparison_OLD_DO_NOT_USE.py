#!/usr/bin/env python3
"""Script to test PDF comparison functionality."""
import json
import sys
import argparse
import asyncio
from pathlib import Path
import pandas as pd
from ai_support_agent.tools.pdf_comparison import PDFComparison
from ai_support_agent.config.config import get_settings


async def main() -> None:
    """Run the comparison test."""
    parser = argparse.ArgumentParser(description="Test PDF comparison")
    parser.add_argument("--json", action="store_true", help="Only output JSON")
    args = parser.parse_args()

    processor = PDFComparison()
    settings = get_settings()

    models = ["520R", "980F"]
    if not args.json:
        print(f"\nComparing models: {', '.join(models)}...")

    try:
        # Get comparison results
        results = await processor.compare_models(models)
        
        if args.json:
            # JSON output only
            print(json.dumps(results.model_dump(), indent=2))
            return
        
        # Display DataFrames
        print("\nFeatures DataFrame:")
        features_data = [
            {"Feature": f.text, **{m: "✓" if present else "" for m, present in f.models.items()}}
            for f in results.features
        ]
        if features_data:
            print(pd.DataFrame(features_data).set_index("Feature"))
        
        print("\nAdvantages DataFrame:")
        advantages_data = [
            {"Advantage": f.text, **{m: "✓" if present else "" for m, present in f.models.items()}}
            for f in results.advantages
        ]
        if advantages_data:
            print(pd.DataFrame(advantages_data).set_index("Advantage"))
        
        print("\nSpecifications DataFrame:")
        specs_data = [
            {
                "Section": s.section,
                "Category": s.category,
                "Specification": s.specification,
                **{m: v.display_value for m, v in s.values.items()}
            }
            for s in results.specifications
        ]
        
        if specs_data:
            print(pd.DataFrame(specs_data))
        
        # Save to file
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        output_path = settings.processed_dir / f"comparison_{timestamp}.json"
        with open(output_path, "w") as f:
            f.write(json.dumps(results.model_dump(), indent=2))
            if not args.json:
                print(f"\nResults saved to {output_path}")

    except Exception as e:
        print(f"Error comparing PDFs: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
