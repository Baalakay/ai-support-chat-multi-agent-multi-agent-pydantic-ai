#!/usr/bin/env python3
"""Script to test PDF processing."""
import json
import argparse
import sys
import pandas as pd
from pathlib import Path
from ai_support_agent.tools.pdf_processor import PDFProcessor
from ai_support_agent.types.pdf import PDFProcessingError
from ai_support_agent.config.config import get_settings


def main() -> None:
    """Run the test."""
    parser = argparse.ArgumentParser(description="Test PDF processing")
    parser.add_argument("--json", action="store_true", help="Only output JSON")
    parser.add_argument("--model", default="520R", help="Model number to process")
    args = parser.parse_args()

    processor = PDFProcessor()
    settings = get_settings()

    # Ensure diagram directory exists
    settings.diagram_dir.mkdir(parents=True, exist_ok=True)

    if not args.json:
        print(f"\nProcessing PDF for model {args.model}...")

    try:
        # Get content using the processor's built-in path handling
        content = processor.get_content(args.model)
        
        if args.json:
            # JSON output only
            result_dict = content.model_dump(exclude={
                'raw_text': True,
                'pages': {'__all__': {'tables': True}}
            })
            print(json.dumps(result_dict, indent=2))
            return

        # Show features and advantages first
        if "Features_And_Advantages" in content.sections:
            section = content.sections["Features_And_Advantages"]
            
            if "features" in section.categories:
                features = section.categories["features"].subcategories[""].value
                print("\nFeatures:")
                for feature in features.split('\n'):
                    if feature.strip():
                        print(f"- {feature.strip()}")
            
            if "advantages" in section.categories:
                advantages = section.categories["advantages"].subcategories[""].value
                print("\nAdvantages:")
                for advantage in advantages.split('\n'):
                    if advantage.strip():
                        print(f"- {advantage.strip()}")
        
        # Convert specifications to DataFrame
        specs_data = []
        for section_name, section in content.sections.items():
            if section_name == "Features_And_Advantages":
                continue
                
            for category_name, category in section.categories.items():
                for spec_name, spec in category.subcategories.items():
                    specs_data.append({
                        "Section": section_name,
                        "Category": category_name,
                        "Specification": spec_name,
                        "Unit": spec.unit or "",
                        "Value": spec.value,
                        "Display": spec.display_value
                    })
        
        if specs_data:
            print("\nSpecifications DataFrame:")
            df = pd.DataFrame(specs_data)
            # Ensure columns are in the correct order
            df = df[["Section", "Category", "Specification", "Unit", "Value", "Display"]]
            print(df.to_string())
        
    except PDFProcessingError as e:
        print(f"Error processing PDF: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
