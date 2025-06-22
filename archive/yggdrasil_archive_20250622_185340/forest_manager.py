#!/usr/bin/env python3
"""
S.IO Forest Manager
Interactive tool for managing the Knowledge Forest
"""

import os
import json
from pathlib import Path
from datetime import datetime

class ForestManager:
    def __init__(self, root_path):
        self.root = Path(root_path)
        
    def show_menu(self):
        """Display main menu"""
        print("\n🌲 S.IO Forest Manager")
        print("=" * 30)
        print("1. 📊 Show Forest Statistics")
        print("2. 🔍 Search Resources")
        print("3. 📚 List Tree Contents") 
        print("4. ➕ Add New Resource")
        print("5. 🔗 Show Cross-References")
        print("6. 📁 Create New Structure")
        print("7. 🧹 Validate Structure")
        print("0. 🚪 Exit")
        
        return input("\nSelect option: ").strip()
    
    def show_statistics(self):
        """Show detailed forest statistics"""
        trees = [d for d in self.root.iterdir() if d.is_dir() and (d / "branches").exists()]
        
        print(f"\n📊 Forest Statistics ({datetime.now().strftime('%Y-%m-%d')})")
        print("=" * 40)
        
        total_branches = total_limbs = total_leafs = 0
        
        for tree_dir in sorted(trees):
            print(f"\n🌳 {tree_dir.name.upper()}")
            
            branches_dir = tree_dir / "branches"
            if branches_dir.exists():
                branches = [d for d in branches_dir.iterdir() if d.is_dir()]
                tree_limbs = tree_leafs = 0
                
                for branch_dir in branches:
                    limbs = [d for d in branch_dir.iterdir() if d.is_dir()]
                    branch_leafs = 0
                    
                    for limb_dir in limbs:
                        leafs = [f for f in limb_dir.iterdir() if f.is_file() and f.suffix == '.json']
                        branch_leafs += len(leafs)
                    
                    tree_limbs += len(limbs)
                    tree_leafs += branch_leafs
                
                print(f"  🌿 Branches: {len(branches)}")
                print(f"  🌱 Limbs: {tree_limbs}")
                print(f"  🍃 Leafs: {tree_leafs}")
                
                total_branches += len(branches)
                total_limbs += tree_limbs
                total_leafs += tree_leafs
        
        print(f"\n🌍 FOREST TOTALS")
        print(f"  🌳 Trees: {len(trees)}")
        print(f"  🌿 Branches: {total_branches}")
        print(f"  🌱 Limbs: {total_limbs}")
        print(f"  🍃 Leafs: {total_leafs}")
    
    def search_resources(self):
        """Search for resources by keyword"""
        query = input("\n🔍 Enter search term: ").lower().strip()
        
        if not query:
            return
        
        results = []
        trees = [d for d in self.root.iterdir() if d.is_dir() and (d / "branches").exists()]
        
        for tree_dir in trees:
            branches_dir = tree_dir / "branches"
            if branches_dir.exists():
                for branch_dir in branches_dir.iterdir():
                    if branch_dir.is_dir():
                        for limb_dir in branch_dir.iterdir():
                            if limb_dir.is_dir():
                                for leaf_file in limb_dir.iterdir():
                                    if leaf_file.is_file() and leaf_file.suffix == '.json':
                                        try:
                                            with open(leaf_file, 'r', encoding='utf-8') as f:
                                                data = json.load(f)
                                                
                                            # Search in various fields
                                            searchable_text = [
                                                data.get('leaf_name', '').lower(),
                                                json.dumps(data.get('resources', [])).lower(),
                                                json.dumps(data.get('metadata', {})).lower()
                                            ]
                                            
                                            if any(query in text for text in searchable_text):
                                                results.append({
                                                    'path': str(leaf_file.relative_to(self.root)),
                                                    'name': data.get('leaf_name', leaf_file.stem),
                                                    'tree_path': data.get('tree_path', 'Unknown')
                                                })
                                        except Exception as e:
                                            continue
        
        print(f"\n🔍 Search Results for '{query}':")
        print("=" * 40)
        
        if results:
            for result in results:
                print(f"📄 {result['name']}")
                print(f"   📍 {result['tree_path']}")
                print(f"   📁 {result['path']}")
                print()
        else:
            print("No results found.")
    
    def list_tree_contents(self):
        """List contents of a specific tree"""
        trees = [d.name for d in self.root.iterdir() if d.is_dir() and (d / "branches").exists()]
        
        print(f"\n🌳 Available Trees:")
        for i, tree in enumerate(trees, 1):
            print(f"{i}. {tree}")
        
        try:
            choice = int(input("\nSelect tree number: ")) - 1
            if 0 <= choice < len(trees):
                self._show_tree_details(trees[choice])
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
    
    def _show_tree_details(self, tree_name):
        """Show detailed contents of a tree"""
        tree_path = self.root / tree_name
        branches_dir = tree_path / "branches"
        
        if not branches_dir.exists():
            print(f"No branches found for {tree_name}")
            return
        
        print(f"\n🌳 {tree_name.upper()} TREE CONTENTS")
        print("=" * 40)
        
        branches = sorted([d for d in branches_dir.iterdir() if d.is_dir()])
        
        for branch_dir in branches:
            print(f"\n🌿 {branch_dir.name}")
            
            limbs = sorted([d for d in branch_dir.iterdir() if d.is_dir()])
            for limb_dir in limbs:
                print(f"  🌱 {limb_dir.name}")
                
                leafs = sorted([f for f in limb_dir.iterdir() if f.is_file() and f.suffix == '.json'])
                for leaf_file in leafs:
                    leaf_name = leaf_file.stem.replace('_leaf', '')
                    print(f"    🍃 {leaf_name}")
    
    def add_new_resource(self):
        """Add a new resource to the forest"""
        print("\n➕ Add New Resource")
        print("=" * 20)
        
        # Get tree
        trees = [d.name for d in self.root.iterdir() if d.is_dir() and (d / "branches").exists()]
        print("Available trees:", ", ".join(trees))
        tree_name = input("Tree name: ").strip()
        
        if tree_name not in trees:
            print("Invalid tree name.")
            return
        
        # Get branch
        tree_path = self.root / tree_name / "branches"
        branches = [d.name for d in tree_path.iterdir() if d.is_dir()]
        print("Available branches:", ", ".join(branches))
        branch_name = input("Branch name: ").strip()
        
        if branch_name not in branches:
            print("Invalid branch name.")
            return
        
        # Get limb
        branch_path = tree_path / branch_name
        limbs = [d.name for d in branch_path.iterdir() if d.is_dir()]
        print("Available limbs:", ", ".join(limbs))
        limb_name = input("Limb name: ").strip()
        
        if limb_name not in limbs:
            create_new = input(f"Limb '{limb_name}' doesn't exist. Create it? (y/n): ").lower()
            if create_new == 'y':
                (branch_path / limb_name).mkdir(exist_ok=True)
                print(f"Created new limb: {limb_name}")
            else:
                return
        
        # Create leaf
        leaf_name = input("Leaf name (without _leaf.json): ").strip()
        if not leaf_name:
            print("Invalid leaf name.")
            return
        
        leaf_file = branch_path / limb_name / f"{leaf_name}_leaf.json"
        
        # Create leaf content
        leaf_data = {
            "limb": limb_name.replace("_", " ").title(),
            "leaf_name": leaf_name.replace("_", " ").title(),
            "leaf_type": "text_collection",
            "tree_path": f"{tree_name.title()} → {branch_name.replace('_', ' ').title()} → {limb_name.replace('_', ' ').title()} → {leaf_name.replace('_', ' ').title()}",
            "resources": [
                {
                    "title": f"Sample {leaf_name.title()} Resource",
                    "author": "To be updated",
                    "category": "general",
                    "description": f"Sample resource for {leaf_name}",
                    "key_concepts": ["concept1", "concept2", "concept3"]
                }
            ],
            "metadata": {
                "total_resources": 1,
                "primary_themes": ["sample_theme"],
                "related_limbs": [],
                "cross_references": []
            }
        }
        
        with open(leaf_file, 'w', encoding='utf-8') as f:
            json.dump(leaf_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created: {leaf_file}")
    
    def validate_structure(self):
        """Validate the forest structure"""
        print("\n🧹 Validating Forest Structure")
        print("=" * 30)
        
        errors = []
        warnings = []
        
        trees = [d for d in self.root.iterdir() if d.is_dir() and (d / "branches").exists()]
        
        for tree_dir in trees:
            # Check tree file exists
            tree_file = tree_dir / f"{tree_dir.name}_tree.json"
            if not tree_file.exists():
                errors.append(f"Missing tree file: {tree_file}")
            
            branches_dir = tree_dir / "branches"
            if branches_dir.exists():
                for branch_dir in branches_dir.iterdir():
                    if branch_dir.is_dir():
                        for limb_dir in branch_dir.iterdir():
                            if limb_dir.is_dir():
                                leafs = [f for f in limb_dir.iterdir() if f.is_file() and f.suffix == '.json']
                                
                                if not leafs:
                                    warnings.append(f"Empty limb: {limb_dir.relative_to(self.root)}")
                                
                                for leaf_file in leafs:
                                    try:
                                        with open(leaf_file, 'r', encoding='utf-8') as f:
                                            data = json.load(f)
                                        
                                        # Validate required fields
                                        required_fields = ['limb', 'leaf_name', 'leaf_type', 'tree_path', 'resources', 'metadata']
                                        for field in required_fields:
                                            if field not in data:
                                                errors.append(f"Missing field '{field}' in {leaf_file.relative_to(self.root)}")
                                    
                                    except json.JSONDecodeError:
                                        errors.append(f"Invalid JSON: {leaf_file.relative_to(self.root)}")
                                    except Exception as e:
                                        errors.append(f"Error reading {leaf_file.relative_to(self.root)}: {e}")
        
        # Show results
        if errors:
            print("❌ ERRORS:")
            for error in errors:
                print(f"  • {error}")
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  • {warning}")
        
        if not errors and not warnings:
            print("✅ Structure validation passed!")
        
        print(f"\n📊 Validation Summary:")
        print(f"  ❌ Errors: {len(errors)}")
        print(f"  ⚠️  Warnings: {len(warnings)}")
    
    def run(self):
        """Run the interactive manager"""
        while True:
            choice = self.show_menu()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                self.show_statistics()
            elif choice == '2':
                self.search_resources()
            elif choice == '3':
                self.list_tree_contents()
            elif choice == '4':
                self.add_new_resource()
            elif choice == '5':
                print("🔗 Cross-reference viewer coming soon!")
            elif choice == '6':
                print("📁 Structure creator coming soon!")
            elif choice == '7':
                self.validate_structure()
            else:
                print("Invalid option. Please try again.")

if __name__ == "__main__":
    root_path = "/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json"
    manager = ForestManager(root_path)
    manager.run()
