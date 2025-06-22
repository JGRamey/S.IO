#!/usr/bin/env python3
"""
S.IO Forest Structure Visualization
Shows the complete Tree→Branches→Limbs→Leafs structure
"""

import os
from pathlib import Path

def show_forest_structure(root_path, max_depth=4):
    """Display the forest structure in a tree-like format"""
    root = Path(root_path)
    
    print("🌲 S.IO Knowledge Forest Structure")
    print("=" * 50)
    print("📁 yggdrasil.json/")
    
    # Get all tree directories
    trees = [d for d in root.iterdir() if d.is_dir() and (d / "branches").exists()]
    
    for tree_dir in sorted(trees):
        print(f"├── 🌳 {tree_dir.name}/")
        print(f"│   ├── {tree_dir.name}_tree.json")
        
        branches_dir = tree_dir / "branches"
        if branches_dir.exists():
            print(f"│   └── 📂 branches/")
            
            branches = [d for d in branches_dir.iterdir() if d.is_dir()]
            for i, branch_dir in enumerate(sorted(branches)):
                is_last_branch = i == len(branches) - 1
                branch_prefix = "└──" if is_last_branch else "├──"
                continuation = "    " if is_last_branch else "│   "
                
                print(f"│       {branch_prefix} 🌿 {branch_dir.name}/")
                
                limbs = [d for d in branch_dir.iterdir() if d.is_dir()]
                for j, limb_dir in enumerate(sorted(limbs)):
                    is_last_limb = j == len(limbs) - 1
                    limb_prefix = "└──" if is_last_limb else "├──"
                    limb_continuation = "    " if is_last_limb else "│   "
                    
                    print(f"│       {continuation}{limb_prefix} 🌱 {limb_dir.name}/")
                    
                    leafs = [f for f in limb_dir.iterdir() if f.is_file() and f.suffix == '.json']
                    for k, leaf_file in enumerate(sorted(leafs)):
                        is_last_leaf = k == len(leafs) - 1
                        leaf_prefix = "└──" if is_last_leaf else "├──"
                        
                        print(f"│       {continuation}{limb_continuation}{leaf_prefix} 🍃 {leaf_file.name}")
        
        print("│")

def count_structure_elements(root_path):
    """Count trees, branches, limbs, and leafs"""
    root = Path(root_path)
    
    trees = [d for d in root.iterdir() if d.is_dir() and (d / "branches").exists()]
    tree_count = len(trees)
    
    branch_count = 0
    limb_count = 0
    leaf_count = 0
    
    for tree_dir in trees:
        branches_dir = tree_dir / "branches"
        if branches_dir.exists():
            branches = [d for d in branches_dir.iterdir() if d.is_dir()]
            branch_count += len(branches)
            
            for branch_dir in branches:
                limbs = [d for d in branch_dir.iterdir() if d.is_dir()]
                limb_count += len(limbs)
                
                for limb_dir in limbs:
                    leafs = [f for f in limb_dir.iterdir() if f.is_file() and f.suffix == '.json']
                    leaf_count += len(leafs)
    
    return tree_count, branch_count, limb_count, leaf_count

if __name__ == "__main__":
    root_path = "/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json"
    
    # Show structure
    show_forest_structure(root_path)
    
    # Show statistics
    trees, branches, limbs, leafs = count_structure_elements(root_path)
    
    print("\n📊 Forest Statistics")
    print("=" * 30)
    print(f"🌳 Trees: {trees}")
    print(f"🌿 Branches: {branches}")
    print(f"🌱 Limbs: {limbs}")
    print(f"🍃 Leafs: {leafs}")
    print(f"📚 Total Resources: {leafs} (individual books/texts/manuscripts)")
    
    print("\n✅ Structure follows: Tree→Branches→Limbs→Leafs")
    print("   - Trees: Main knowledge domains")
    print("   - Branches: Major subdivisions within each tree")
    print("   - Limbs: Specific categories within branches")
    print("   - Leafs: Individual resources/texts (the actual data sources)")
