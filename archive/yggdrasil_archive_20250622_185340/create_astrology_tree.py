#!/usr/bin/env python3
"""
Create Astrology Tree Structure
Builds comprehensive astrology tree following Tree→Branches→Limbs→Leafs pattern
"""

import os
import json
from pathlib import Path

def create_astrology_structure():
    """Create the complete astrology tree structure"""
    root = Path("/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json")
    
    # Define astrology structure
    astrology_structure = {
        "tree_file": "astrology_tree.json",
        "branches": {
            "western_astrology": {
                "limbs": {
                    "classical_astrology": [
                        "ptolemy_tetrabiblos_leaf.json",
                        "medieval_texts_leaf.json",
                        "renaissance_astrology_leaf.json"
                    ],
                    "modern_astrology": [
                        "psychological_astrology_leaf.json",
                        "evolutionary_astrology_leaf.json",
                        "contemporary_methods_leaf.json"
                    ],
                    "horary_astrology": [
                        "william_lilly_leaf.json",
                        "horary_techniques_leaf.json",
                        "electional_astrology_leaf.json"
                    ]
                }
            },
            "vedic_astrology": {
                "limbs": {
                    "classical_texts": [
                        "brihat_parashara_hora_leaf.json",
                        "jaimini_sutras_leaf.json",
                        "saravali_texts_leaf.json"
                    ],
                    "computational_methods": [
                        "dasha_systems_leaf.json",
                        "divisional_charts_leaf.json",
                        "planetary_periods_leaf.json"
                    ],
                    "predictive_techniques": [
                        "transit_analysis_leaf.json",
                        "varshphal_methods_leaf.json",
                        "mundane_astrology_leaf.json"
                    ]
                }
            },
            "chinese_astrology": {
                "limbs": {
                    "classical_systems": [
                        "four_pillars_leaf.json",
                        "zi_wei_dou_shu_leaf.json",
                        "chinese_calendar_leaf.json"
                    ],
                    "feng_shui_astrology": [
                        "flying_stars_leaf.json",
                        "landscape_astrology_leaf.json",
                        "directional_systems_leaf.json"
                    ],
                    "traditional_texts": [
                        "ancient_chronicles_leaf.json",
                        "imperial_records_leaf.json",
                        "taoist_astrology_leaf.json"
                    ]
                }
            },
            "natal_astrology": {
                "limbs": {
                    "chart_interpretation": [
                        "birth_chart_analysis_leaf.json",
                        "aspect_patterns_leaf.json",
                        "planetary_dignities_leaf.json"
                    ],
                    "house_systems": [
                        "placidus_system_leaf.json",
                        "whole_sign_houses_leaf.json",
                        "equal_house_system_leaf.json"
                    ],
                    "timing_techniques": [
                        "progressions_leaf.json",
                        "solar_returns_leaf.json",
                        "lunar_returns_leaf.json"
                    ]
                }
            },
            "mundane_astrology": {
                "limbs": {
                    "political_astrology": [
                        "national_charts_leaf.json",
                        "election_astrology_leaf.json",
                        "world_events_leaf.json"
                    ],
                    "economic_astrology": [
                        "market_cycles_leaf.json",
                        "commodity_astrology_leaf.json",
                        "financial_forecasting_leaf.json"
                    ],
                    "natural_disasters": [
                        "earthquake_prediction_leaf.json",
                        "weather_astrology_leaf.json",
                        "climate_patterns_leaf.json"
                    ]
                }
            },
            "esoteric_astrology": {
                "limbs": {
                    "soul_astrology": [
                        "alice_bailey_leaf.json",
                        "spiritual_development_leaf.json",
                        "ray_astrology_leaf.json"
                    ],
                    "karmic_astrology": [
                        "past_life_indicators_leaf.json",
                        "lunar_nodes_leaf.json",
                        "evolutionary_purpose_leaf.json"
                    ],
                    "hermetic_astrology": [
                        "alchemical_astrology_leaf.json",
                        "kabbalalistic_astrology_leaf.json",
                        "mystery_school_teachings_leaf.json"
                    ]
                }
            }
        }
    }
    
    # Create astrology tree directory
    astrology_path = root / "astrology"
    astrology_path.mkdir(exist_ok=True)
    
    print("🌟 Creating Astrology Tree Structure...")
    
    # Create tree file
    tree_data = {
        "tree_name": "Astrology",
        "description": "Comprehensive collection of astrological knowledge, techniques, and traditions",
        "branches": list(astrology_structure["branches"].keys()),
        "metadata": {
            "created": "2025-06-22",
            "structure_version": "1.0",
            "total_branches": len(astrology_structure["branches"]),
            "traditions_covered": ["Western", "Vedic", "Chinese", "Esoteric"],
            "scope": "Classical texts, modern methods, predictive techniques, and spiritual astrology"
        }
    }
    
    tree_file_path = astrology_path / "astrology_tree.json"
    with open(tree_file_path, 'w', encoding='utf-8') as f:
        json.dump(tree_data, f, indent=2, ensure_ascii=False)
    print(f"✨ Created: {tree_file_path}")
    
    # Create branches directory
    branches_path = astrology_path / "branches"
    branches_path.mkdir(exist_ok=True)
    
    # Create each branch with its limbs and leafs
    for branch_name, branch_config in astrology_structure["branches"].items():
        branch_path = branches_path / branch_name
        branch_path.mkdir(exist_ok=True)
        
        print(f"🌿 Creating branch: {branch_name}")
        
        # Create limbs within each branch
        for limb_name, leaf_files in branch_config["limbs"].items():
            limb_path = branch_path / limb_name
            limb_path.mkdir(exist_ok=True)
            
            print(f"  🌱 Creating limb: {limb_name}")
            
            # Create leaf files within each limb
            for leaf_file in leaf_files:
                leaf_path = limb_path / leaf_file
                create_astrology_leaf_file(leaf_path, branch_name, limb_name)
                print(f"    🍃 Created: {leaf_file}")
    
    print("🌟 Astrology tree structure created successfully!")

def create_astrology_leaf_file(file_path, branch_name, limb_name):
    """Create an astrology-specific leaf file"""
    leaf_name = file_path.stem.replace("_leaf", "").replace("_", " ").title()
    
    # Enhanced content for specific astrology leafs
    enhanced_leafs = {
        "ptolemy_tetrabiblos": {
            "resources": [
                {
                    "title": "Tetrabiblos",
                    "author": "Claudius Ptolemy",
                    "category": "classical_foundation",
                    "description": "Foundational text of Western astrology, establishing the four-book system",
                    "key_concepts": ["four_elements", "planetary_qualities", "houses", "aspects", "mundane_astrology"]
                }
            ]
        },
        "brihat_parashara_hora": {
            "resources": [
                {
                    "title": "Brihat Parashara Hora Shastra",
                    "author": "Sage Parashara",
                    "category": "vedic_foundation",
                    "description": "Fundamental text of Vedic astrology covering all major techniques",
                    "key_concepts": ["rashis", "nakshatras", "dashas", "yogas", "divisional_charts"]
                }
            ]
        },
        "four_pillars": {
            "resources": [
                {
                    "title": "Four Pillars of Destiny",
                    "author": "Traditional Chinese Astrologers",
                    "category": "chinese_system",
                    "description": "Ba Zi system using year, month, day, and hour pillars for destiny analysis",
                    "key_concepts": ["heavenly_stems", "earthly_branches", "five_elements", "luck_pillars"]
                }
            ]
        }
    }
    
    # Get enhanced content or create default
    leaf_key = file_path.stem.replace("_leaf", "")
    if leaf_key in enhanced_leafs:
        resources = enhanced_leafs[leaf_key]["resources"]
    else:
        resources = [
            {
                "title": f"Sample {leaf_name} Resource",
                "author": "Traditional Astrologers",
                "category": "astrological_text",
                "description": f"Traditional and modern sources on {leaf_name.lower()}",
                "key_concepts": ["astrology", "prediction", "interpretation"]
            }
        ]
    
    leaf_data = {
        "limb": limb_name.replace("_", " ").title(),
        "leaf_name": leaf_name,
        "leaf_type": "astrological_texts",
        "tree_path": f"Astrology → {branch_name.replace('_', ' ').title()} → {limb_name.replace('_', ' ').title()} → {leaf_name}",
        "resources": resources,
        "metadata": {
            "total_resources": len(resources),
            "primary_themes": ["astrology", "divination", "celestial_influence"],
            "related_limbs": [],
            "cross_references": ["astronomy", "mathematics", "philosophy", "religion"]
        }
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(leaf_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    create_astrology_structure()
