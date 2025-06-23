#!/usr/bin/env python3
"""
S.IO Directory Navigation Helper
Quick access to important files and folders
"""

import os
import sys
from pathlib import Path

def get_project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent

def print_structure():
    """Print the organized directory structure"""
    root = get_project_root()
    
    print("🗂️  S.IO ORGANIZED DIRECTORY STRUCTURE")
    print("="*50)
    
    important_paths = {
        "📄 Main README": "README.md",
        "📄 Directory Guide": "DIRECTORY_STRUCTURE.md",
        "🧠 Core Application": "yggdrasil/",
        "🔗 MCP Server": "mcp/server/yggdrasil_mcp_server.py",
        "🔗 MCP Client": "mcp/client/yggdrasil_mcp_client.py",
        "⚙️  Configuration": "config/",
        "🗃️  Database Schemas": "sql/",
        "🧪 Tests": "tests/",
        "📚 Documentation": "docs/guides/",
        "🔧 Scripts": "scripts/",
        "🚀 Deployment": "deployment/docker/",
        "📖 Examples": "examples/",
        "📦 Archive": "archive/",
    }
    
    for name, path in important_paths.items():
        full_path = root / path
        exists = "✅" if full_path.exists() else "❌"
        print(f"{exists} {name:<20} → {path}")
    
    print("\n🎯 QUICK ACCESS COMMANDS:")
    print("-" * 30)
    print("• Test system:     python3 tests/quick_agent_test.py")
    print("• MCP agents:      python3 tests/test_mcp_agents.py")
    print("• Start Docker:    docker-compose -f deployment/docker/docker-compose.yml up -d")
    print("• View docs:       open docs/guides/")
    print("• MCP guide:       open docs/guides/MCP_AGENTS_GUIDE.md")

def show_file_info(file_path):
    """Show information about a specific file"""
    root = get_project_root()
    full_path = root / file_path
    
    if not full_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📄 {file_path}")
    print("-" * len(file_path))
    
    if full_path.is_file():
        size = full_path.stat().st_size
        print(f"Size: {size:,} bytes")
        
        # Try to show first few lines for text files
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:5]
                print(f"Lines: {len(lines)} (showing first 5)")
                print("Content preview:")
                for i, line in enumerate(lines, 1):
                    print(f"{i:2d}: {line.rstrip()}")
        except:
            print("Binary file or encoding issue")
    
    elif full_path.is_dir():
        items = list(full_path.iterdir())
        print(f"Contains {len(items)} items")
        
        for item in sorted(items)[:10]:  # Show first 10 items
            icon = "📁" if item.is_dir() else "📄"
            print(f"  {icon} {item.name}")
        
        if len(items) > 10:
            print(f"  ... and {len(items) - 10} more items")

def main():
    """Main navigation function"""
    if len(sys.argv) < 2:
        print_structure()
        return
    
    command = sys.argv[1].lower()
    
    if command == "info" and len(sys.argv) > 2:
        show_file_info(sys.argv[2])
    elif command == "structure":
        print_structure()
    elif command == "help":
        print("S.IO Navigation Helper")
        print("Usage:")
        print("  python3 navigate.py                 # Show directory structure")
        print("  python3 navigate.py structure       # Show directory structure") 
        print("  python3 navigate.py info <path>     # Show file/folder info")
        print("  python3 navigate.py help            # Show this help")
    else:
        print(f"Unknown command: {command}")
        print("Use 'python3 navigate.py help' for usage information")

if __name__ == "__main__":
    main()
