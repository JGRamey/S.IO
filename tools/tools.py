#!/usr/bin/env python3
"""
S.IO Simple Tools
Basic utilities for the consolidated project
"""

import json
from pathlib import Path

def show_structure():
    """Show knowledge structure summary"""
    schema_path = Path(__file__).parent.parent / "schema" / "knowledge_structure.json"
    
    if schema_path.exists():
        with open(schema_path, 'r') as f:
            structure = json.load(f)
        
        print("KNOWLEDGE STRUCTURE SUMMARY")
        print("=" * 30)
        print(f"Trees: {len(structure.get('trees', {}))}")
        
        for tree_name in structure.get('trees', {}):
            print(f"  - {tree_name}")
    else:
        print("Structure file not found")

def validate_schema():
    """Check if schema files exist"""
    schema_dir = Path(__file__).parent.parent / "schema"
    required_files = ["schema.sql", "models.py", "api_example.py"]
    
    print("SCHEMA VALIDATION")
    print("=" * 20)
    
    for file_name in required_files:
        file_path = schema_dir / file_name
        status = "✓" if file_path.exists() else "✗"
        print(f"{status} {file_name}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tools.py [command]")
        print("Commands: structure, validate")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "structure":
        show_structure()
    elif command == "validate":
        validate_schema()
    else:
        print(f"Unknown command: {command}")
