#!/usr/bin/env python3
"""
Export OpenAPI schema from FastAPI app.
Usage: python scripts/export_openapi.py [--output openapi.json]
"""
import argparse
import json
import sys
import os

# Add api/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))


def main():
    parser = argparse.ArgumentParser(description="Export ITOps Platform OpenAPI schema")
    parser.add_argument("--output", "-o", default="openapi.json", help="Output file path")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    # Import FastAPI app after path setup
    try:
        from main import app
    except ImportError as e:
        print(f"ERROR: Could not import api.main: {e}")
        print("Make sure you are running from the project root or api/ directory")
        sys.exit(1)

    schema = app.openapi()

    # Ensure version field exists
    if "info" not in schema:
        schema["info"] = {}
    schema["info"]["title"] = schema["info"].get("title", "ITOps Platform API")
    schema["info"]["version"] = schema["info"].get("version", "1.0.0")

    indent = 2 if args.pretty else None
    output_path = args.output

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=indent, ensure_ascii=False)

    size = os.path.getsize(output_path)
    print(f"OpenAPI schema exported to {output_path} ({size} bytes)")
    print(f"  Title: {schema['info']['title']}")
    print(f"  Version: {schema['info']['version']}")
    print(f"  Paths: {len(schema.get('paths', {}))}")


if __name__ == "__main__":
    main()
