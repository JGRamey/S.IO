#!/usr/bin/env python3
"""
Display Astrology Tree Structure
Shows the complete astrology tree in detail
"""

from pathlib import Path

def show_astrology_structure():
    """Display the astrology tree structure"""
    root = Path("/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json")
    astrology_path = root / "astrology"
    
    if not astrology_path.exists():
        print("❌ Astrology tree not found!")
        return
    
    print("🌟 ASTROLOGY TREE STRUCTURE")
    print("=" * 50)
    print("📁 astrology/")
    print("├── astrology_tree.json")
    
    branches_dir = astrology_path / "branches"
    if branches_dir.exists():
        print("└── 📂 branches/")
        
        branches = sorted([d for d in branches_dir.iterdir() if d.is_dir()])
        
        for i, branch_dir in enumerate(branches):
            is_last_branch = i == len(branches) - 1
            branch_prefix = "└──" if is_last_branch else "├──"
            continuation = "    " if is_last_branch else "│   "
            
            print(f"    {branch_prefix} 🌿 {branch_dir.name}/")
            
            limbs = sorted([d for d in branch_dir.iterdir() if d.is_dir()])
            for j, limb_dir in enumerate(limbs):
                is_last_limb = j == len(limbs) - 1
                limb_prefix = "└──" if is_last_limb else "├──"
                limb_continuation = "    " if is_last_limb else "│   "
                
                print(f"    {continuation}{limb_prefix} 🌱 {limb_dir.name}/")
                
                leafs = sorted([f for f in limb_dir.iterdir() if f.is_file() and f.suffix == '.json'])
                for k, leaf_file in enumerate(leafs):
                    is_last_leaf = k == len(leafs) - 1
                    leaf_prefix = "└──" if is_last_leaf else "├──"
                    
                    print(f"    {continuation}{limb_continuation}{leaf_prefix} 🍃 {leaf_file.name}")
    
    # Count statistics
    branches = [d for d in branches_dir.iterdir() if d.is_dir()]
    branch_count = len(branches)
    limb_count = 0
    leaf_count = 0
    
    for branch_dir in branches:
        limbs = [d for d in branch_dir.iterdir() if d.is_dir()]
        limb_count += len(limbs)
        
        for limb_dir in limbs:
            leafs = [f for f in limb_dir.iterdir() if f.is_file() and f.suffix == '.json']
            leaf_count += len(leafs)
    
    print(f"\n🌟 ASTROLOGY TREE STATISTICS")
    print("=" * 30)
    print(f"🌿 Branches: {branch_count}")
    print(f"🌱 Limbs: {limb_count}")
    print(f"🍃 Leafs: {leaf_count}")
    print(f"📚 Astrological Resources: {leaf_count}")
    
    print(f"\n📖 BRANCHES COVERED:")
    for branch_dir in branches:
        branch_name = branch_dir.name.replace("_", " ").title()
        print(f"  • {branch_name}")

if __name__ == "__main__":
    show_astrology_structure()
