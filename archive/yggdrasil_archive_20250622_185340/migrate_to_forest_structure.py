#!/usr/bin/env python3
"""
S.IO Knowledge Forest Migration Script

This script helps migrate existing JSON files to the new Tree/Branch/Limb/Leaf structure.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

class ForestMigrator:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.trees_path = self.base_path / "trees.json"
        self.legacy_files = []
        self.migration_log = []
        
    def scan_legacy_files(self) -> List[str]:
        """Scan for legacy JSON files that need migration."""
        legacy_patterns = ["*.json"]
        legacy_files = []
        
        for pattern in legacy_patterns:
            legacy_files.extend(self.trees_path.glob(pattern))
            
        # Exclude already migrated files
        exclude_patterns = [
            "master_tree_structure.json",
            "*_branches.json", 
            "*_leaf.json"
        ]
        
        filtered_files = []
        for file in legacy_files:
            if not any(file.match(pattern) for pattern in exclude_patterns):
                filtered_files.append(file)
                
        return filtered_files
    
    def analyze_legacy_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a legacy JSON file to determine its tree classification."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            analysis = {
                "file_path": file_path,
                "file_name": file_path.name,
                "contains_field": "field" in data,
                "contains_subfields": "subfields" in data,
                "field_name": data.get("field", "Unknown"),
                "subfield_count": len(data.get("subfields", [])),
                "suggested_tree": self.suggest_tree_classification(file_path.stem),
                "content": data
            }
            
            return analysis
            
        except Exception as e:
            return {
                "file_path": file_path,
                "error": str(e),
                "suggested_tree": "unknown"
            }
    
    def suggest_tree_classification(self, filename: str) -> str:
        """Suggest which tree a file belongs to based on filename."""
        tree_mappings = {
            "philosophy": "philosophy_tree",
            "religion": "religion_tree", 
            "science": "science_tree",
            "math": "science_tree",
            "physics": "science_tree",
            "quantum": "science_tree",
            "history": "history_tree",
            "literature": "literature_tree",
            "art": "arts_tree",
            "psychology": "science_tree",
            "neuroscience": "science_tree",
            "ai": "science_tree",
            "machine_learning": "science_tree",
            "data": "science_tree"
        }
        
        filename_lower = filename.lower()
        for key, tree in tree_mappings.items():
            if key in filename_lower:
                return tree
                
        return "unknown_tree"
    
    def create_leaf_from_legacy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legacy file content to leaf structure."""
        content = analysis.get("content", {})
        
        leaf_structure = {
            "limb": "Legacy Content",
            "leaf_name": analysis["file_name"].replace(".json", "").replace("_", " ").title(),
            "leaf_type": "migrated_content",
            "tree_path": f"{analysis['suggested_tree']} → Legacy → {analysis['file_name']}",
            "resources": [],
            "metadata": {
                "migrated_from": str(analysis["file_path"]),
                "original_field": content.get("field", ""),
                "migration_date": "2025-06-22",
                "requires_review": True
            }
        }
        
        # Convert subfields to resources if present
        if "subfields" in content:
            for subfield in content["subfields"]:
                resource = {
                    "title": subfield,
                    "category": "subfield",
                    "description": f"Subfield from legacy {analysis['file_name']}"
                }
                leaf_structure["resources"].append(resource)
        
        return leaf_structure
    
    def run_migration(self, dry_run=True) -> Dict[str, Any]:
        """Run the complete migration process."""
        print("🌳 Starting S.IO Knowledge Forest Migration")
        print("=" * 50)
        
        # Scan for legacy files
        legacy_files = self.scan_legacy_files()
        print(f"Found {len(legacy_files)} legacy files to analyze")
        
        migration_report = {
            "total_files": len(legacy_files),
            "successful_migrations": 0,
            "failed_migrations": 0,
            "tree_distribution": {},
            "files_processed": []
        }
        
        for file_path in legacy_files:
            print(f"\n📁 Analyzing: {file_path.name}")
            
            # Analyze the file
            analysis = self.analyze_legacy_file(file_path)
            
            if "error" in analysis:
                print(f"❌ Error analyzing {file_path.name}: {analysis['error']}")
                migration_report["failed_migrations"] += 1
                continue
            
            # Track tree distribution
            tree = analysis["suggested_tree"]
            migration_report["tree_distribution"][tree] = migration_report["tree_distribution"].get(tree, 0) + 1
            
            print(f"   📊 Field: {analysis['field_name']}")
            print(f"   🌿 Subfields: {analysis['subfield_count']}")
            print(f"   🌳 Suggested Tree: {tree}")
            
            # Create leaf structure
            leaf_data = self.create_leaf_from_legacy(analysis)
            
            if not dry_run:
                # Create the actual leaf file
                leaf_filename = f"{file_path.stem}_migrated_leaf.json"
                leaf_path = self.trees_path / "migrated_content" / leaf_filename
                
                # Ensure directory exists
                leaf_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    with open(leaf_path, 'w', encoding='utf-8') as f:
                        json.dump(leaf_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"   ✅ Created leaf: {leaf_filename}")
                    migration_report["successful_migrations"] += 1
                    
                except Exception as e:
                    print(f"   ❌ Failed to create leaf: {e}")
                    migration_report["failed_migrations"] += 1
            else:
                print(f"   🔍 [DRY RUN] Would create: {file_path.stem}_migrated_leaf.json")
                migration_report["successful_migrations"] += 1
            
            migration_report["files_processed"].append({
                "file": file_path.name,
                "tree": tree,
                "status": "success" if "error" not in analysis else "failed"
            })
        
        # Print summary
        print("\n" + "=" * 50)
        print("🌲 Migration Summary")
        print("=" * 50)
        print(f"Total files processed: {migration_report['total_files']}")
        print(f"Successful migrations: {migration_report['successful_migrations']}")
        print(f"Failed migrations: {migration_report['failed_migrations']}")
        
        print("\n🌳 Tree Distribution:")
        for tree, count in migration_report["tree_distribution"].items():
            print(f"   {tree}: {count} files")
        
        if dry_run:
            print("\n⚠️  This was a DRY RUN - no files were actually created.")
            print("Run with dry_run=False to perform actual migration.")
        
        return migration_report

def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_forest_structure.py <path_to_s.io_directory> [--execute]")
        sys.exit(1)
    
    base_path = sys.argv[1]
    execute = "--execute" in sys.argv
    
    migrator = ForestMigrator(base_path)
    report = migrator.run_migration(dry_run=not execute)
    
    if execute:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n🔍 Analysis completed. Use --execute flag to perform actual migration.")

if __name__ == "__main__":
    main()
