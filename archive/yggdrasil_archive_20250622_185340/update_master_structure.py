#!/usr/bin/env python3
"""
Update Master Structure File
Updates the master structure to include all current trees
"""

import json
from pathlib import Path

def update_master_structure():
    """Update the master structure file with current forest state"""
    root = Path("/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json")
    
    master_structure = {
        "forest_name": "S.IO Knowledge Forest",
        "version": "2.1",
        "restructure_date": "2025-06-22",
        "structure_type": "Tree→Branches→Limbs→Leafs",
        "trees": {}
    }
    
    # Scan actual structure and populate master file
    trees = [d for d in root.iterdir() if d.is_dir() and (d / "branches").exists()]
    
    for tree_dir in sorted(trees):
        print(f"📊 Scanning tree: {tree_dir.name}")
        master_structure["trees"][tree_dir.name] = scan_tree_structure(tree_dir)
    
    # Write updated master file
    master_file = root / "master_tree_structure.json"
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(master_structure, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated master structure file: {master_file}")
    
    # Show summary
    total_branches = sum(len(tree_data["branches"]) for tree_data in master_structure["trees"].values())
    total_limbs = sum(
        sum(len(branch_data["limbs"]) for branch_data in tree_data["branches"].values())
        for tree_data in master_structure["trees"].values()
    )
    total_leafs = sum(
        sum(
            sum(len(limb_leafs) for limb_leafs in branch_data["limbs"].values())
            for branch_data in tree_data["branches"].values()
        )
        for tree_data in master_structure["trees"].values()
    )
    
    print(f"\n🌍 UPDATED FOREST TOTALS:")
    print(f"  🌳 Trees: {len(master_structure['trees'])}")
    print(f"  🌿 Branches: {total_branches}")
    print(f"  🌱 Limbs: {total_limbs}")
    print(f"  🍃 Leafs: {total_leafs}")

def scan_tree_structure(tree_path):
    """Scan and document the structure of a tree"""
    structure = {"branches": {}}
    branches_path = tree_path / "branches"
    
    if branches_path.exists():
        for branch_dir in branches_path.iterdir():
            if branch_dir.is_dir():
                structure["branches"][branch_dir.name] = {"limbs": {}}
                
                for limb_dir in branch_dir.iterdir():
                    if limb_dir.is_dir():
                        limb_leafs = []
                        for leaf_file in limb_dir.iterdir():
                            if leaf_file.is_file() and leaf_file.suffix == '.json':
                                limb_leafs.append(leaf_file.name)
                        structure["branches"][branch_dir.name]["limbs"][limb_dir.name] = sorted(limb_leafs)
    
    return structure

if __name__ == "__main__":
    update_master_structure()
