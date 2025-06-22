#!/usr/bin/env python3
"""
S.IO Legacy File Cleanup
Moves remaining legacy files to organized locations or archive
"""

import os
import json
import shutil
from pathlib import Path

def cleanup_legacy_files():
    """Clean up and organize remaining legacy files"""
    root = Path("/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json")
    
    # Files to move to archive
    legacy_files = [
        "antiquity.json",
        "psychology.json", 
        "quantum_com.json",
        "quantum_mech.json", 
        "quantum_phys.json",
        "language_tree.json",
        "1fields.md",
        "subfields_restructure_plan.md"
    ]
    
    # Create archive directory
    archive_dir = root / "archive_legacy_files"
    archive_dir.mkdir(exist_ok=True)
    
    print("🧹 Cleaning up legacy files...")
    
    for legacy_file in legacy_files:
        legacy_path = root / legacy_file
        if legacy_path.exists():
            archive_path = archive_dir / legacy_file
            shutil.move(str(legacy_path), str(archive_path))
            print(f"📦 Moved {legacy_file} to archive")
    
    # Handle remaining directories that don't fit the structure
    legacy_dirs = ["astrology", "math"]
    
    for legacy_dir in legacy_dirs:
        legacy_path = root / legacy_dir
        if legacy_path.exists():
            archive_path = archive_dir / legacy_dir
            if archive_path.exists():
                shutil.rmtree(archive_path)
            shutil.move(str(legacy_path), str(archive_path))
            print(f"📁 Moved {legacy_dir}/ directory to archive")
    
    print("✅ Legacy cleanup complete!")

def enhance_leaf_content():
    """Enhance leaf files with more realistic content"""
    root = Path("/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json")
    
    # Enhanced content for specific important leafs
    enhanced_content = {
        "philosophy/branches/ancient_philosophy/greek_philosophy/plato_works_leaf.json": {
            "limb": "Greek Philosophy",
            "leaf_name": "Plato Works",
            "leaf_type": "philosophical_texts",
            "tree_path": "Philosophy → Ancient Philosophy → Greek Philosophy → Plato Works",
            "resources": [
                {
                    "title": "The Republic",
                    "author": "Plato",
                    "category": "political_philosophy",
                    "description": "Plato's most famous dialogue examining justice and the ideal state",
                    "key_concepts": ["justice", "philosopher_kings", "allegory_of_cave", "theory_of_forms", "tripartite_soul"]
                },
                {
                    "title": "The Apology",
                    "author": "Plato", 
                    "category": "socratic_dialogue",
                    "description": "Socrates' defense speech at his trial for corrupting youth and impiety",
                    "key_concepts": ["socratic_method", "virtue", "wisdom", "examined_life", "divine_mission"]
                },
                {
                    "title": "Phaedo",
                    "author": "Plato",
                    "category": "metaphysics",
                    "description": "Dialogue on the immortality of the soul and Socrates' final hours",
                    "key_concepts": ["soul_immortality", "theory_of_forms", "recollection", "death", "philosophical_life"]
                },
                {
                    "title": "Meno",
                    "author": "Plato",
                    "category": "epistemology", 
                    "description": "Exploration of learning, knowledge, and virtue through geometric demonstration",
                    "key_concepts": ["learning_paradox", "recollection", "virtue", "geometry_lesson", "a_priori_knowledge"]
                },
                {
                    "title": "Timaeus",
                    "author": "Plato",
                    "category": "cosmology",
                    "description": "Plato's account of the creation and structure of the universe",
                    "key_concepts": ["demiurge", "cosmic_order", "geometrical_atoms", "world_soul", "receptacle"]
                }
            ],
            "metadata": {
                "total_works": 5,
                "primary_themes": ["metaphysics", "epistemology", "political_philosophy", "ethics"],
                "related_limbs": ["aristotle_works", "socratic_dialogues", "presocratic_fragments"],
                "cross_references": ["virtue_ethics", "political_philosophy", "metaphysics", "theory_of_forms"]
            }
        },
        
        "religion/branches/christianity/biblical_texts/new_testament_leaf.json": {
            "limb": "Biblical Texts",
            "leaf_name": "New Testament",
            "leaf_type": "sacred_scripture",
            "tree_path": "Religion → Christianity → Biblical Texts → New Testament",
            "resources": [
                {
                    "title": "Gospel of Matthew",
                    "author": "Traditional: Matthew the Apostle",
                    "category": "gospel",
                    "description": "First Gospel presenting Jesus as the Jewish Messiah",
                    "key_concepts": ["messianic_prophecy", "sermon_on_mount", "kingdom_of_heaven", "genealogy"]
                },
                {
                    "title": "Gospel of Mark", 
                    "author": "Traditional: John Mark",
                    "category": "gospel",
                    "description": "Earliest Gospel emphasizing Jesus' actions and suffering",
                    "key_concepts": ["messianic_secret", "discipleship", "passion_narrative", "divine_sonship"]
                },
                {
                    "title": "Gospel of Luke",
                    "author": "Traditional: Luke the Physician", 
                    "category": "gospel",
                    "description": "Gospel emphasizing Jesus' compassion for outcasts and universal salvation",
                    "key_concepts": ["social_justice", "gentile_mission", "holy_spirit", "prayer"]
                },
                {
                    "title": "Gospel of John",
                    "author": "Traditional: John the Apostle",
                    "category": "gospel", 
                    "description": "Theological Gospel presenting Jesus as the divine Word",
                    "key_concepts": ["logos", "eternal_life", "i_am_sayings", "divine_nature"]
                },
                {
                    "title": "Acts of the Apostles",
                    "author": "Traditional: Luke the Physician",
                    "category": "historical_narrative",
                    "description": "History of the early Christian church and mission",
                    "key_concepts": ["pentecost", "gentile_mission", "paul_conversion", "church_growth"]
                },
                {
                    "title": "Romans",
                    "author": "Paul the Apostle", 
                    "category": "pauline_epistle",
                    "description": "Paul's systematic exposition of Christian theology",
                    "key_concepts": ["justification_by_faith", "sin_and_salvation", "predestination", "law_and_grace"]
                },
                {
                    "title": "Revelation",
                    "author": "Traditional: John of Patmos",
                    "category": "apocalyptic_literature",
                    "description": "Prophetic vision of the end times and Christ's return", 
                    "key_concepts": ["apocalypse", "seven_churches", "beast", "new_jerusalem"]
                }
            ],
            "metadata": {
                "total_works": 27,
                "primary_themes": ["salvation", "christology", "eschatology", "church_formation"],
                "related_limbs": ["old_testament", "patristic_literature", "denominational_texts"],
                "cross_references": ["christian_theology", "biblical_interpretation", "church_history"]
            }
        }
    }
    
    print("📚 Enhancing leaf content...")
    
    for file_path, content in enhanced_content.items():
        full_path = root / file_path
        if full_path.exists():
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            print(f"✨ Enhanced: {file_path}")
    
    print("✅ Content enhancement complete!")

if __name__ == "__main__":
    cleanup_legacy_files()
    enhance_leaf_content()
