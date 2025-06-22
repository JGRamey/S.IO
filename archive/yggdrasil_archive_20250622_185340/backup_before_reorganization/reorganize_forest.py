#!/usr/bin/env python3
"""
S.IO Forest Reorganization Script
Restructures the knowledge database following the Tree→Branches→Limbs→Leafs pattern
"""

import os
import json
import shutil
from pathlib import Path

class ForestReorganizer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.backup_path = self.root_path / "backup_before_reorganization"
        
    def create_backup(self):
        """Create backup of current structure"""
        if self.backup_path.exists():
            shutil.rmtree(self.backup_path)
        
        print("Creating backup...")
        shutil.copytree(self.root_path, self.backup_path, 
                       ignore=shutil.ignore_patterns('backup_*', '__pycache__', '*.pyc'))
        print(f"Backup created at: {self.backup_path}")
    
    def get_ideal_structure(self):
        """Define the ideal forest structure"""
        return {
            "philosophy": {
                "tree_file": "philosophy_tree.json",
                "branches": {
                    "ancient_philosophy": {
                        "limbs": {
                            "greek_philosophy": ["plato_works_leaf.json", "aristotle_works_leaf.json", "socratic_dialogues_leaf.json"],
                            "roman_philosophy": ["stoic_texts_leaf.json", "cicero_works_leaf.json"],
                            "hellenistic_philosophy": ["epicurean_texts_leaf.json", "skeptic_texts_leaf.json"]
                        }
                    },
                    "medieval_philosophy": {
                        "limbs": {
                            "scholasticism": ["aquinas_works_leaf.json", "augustine_works_leaf.json"],
                            "islamic_philosophy": ["averroes_works_leaf.json", "avicenna_works_leaf.json"],
                            "jewish_philosophy": ["maimonides_works_leaf.json"]
                        }
                    },
                    "modern_philosophy": {
                        "limbs": {
                            "rationalism": ["descartes_works_leaf.json", "spinoza_works_leaf.json"],
                            "empiricism": ["hume_works_leaf.json", "locke_works_leaf.json"],
                            "german_idealism": ["kant_works_leaf.json", "hegel_works_leaf.json"]
                        }
                    },
                    "contemporary_philosophy": {
                        "limbs": {
                            "analytic_philosophy": ["russell_works_leaf.json", "wittgenstein_works_leaf.json"],
                            "continental_philosophy": ["heidegger_works_leaf.json", "sartre_works_leaf.json"],
                            "existentialism": ["kierkegaard_works_leaf.json", "nietzsche_works_leaf.json"]
                        }
                    }
                }
            },
            "religion": {
                "tree_file": "religion_tree.json",
                "branches": {
                    "christianity": {
                        "limbs": {
                            "biblical_texts": ["old_testament_leaf.json", "new_testament_leaf.json", "apocrypha_leaf.json"],
                            "patristic_literature": ["church_fathers_leaf.json", "apostolic_fathers_leaf.json"],
                            "denominational_texts": ["catholic_catechism_leaf.json", "protestant_confessions_leaf.json", "orthodox_texts_leaf.json"]
                        }
                    },
                    "islam": {
                        "limbs": {
                            "islamic_texts": ["quran_leaf.json", "hadith_collections_leaf.json"],
                            "islamic_philosophy": ["kalam_texts_leaf.json", "sufi_literature_leaf.json"],
                            "jurisprudence": ["fiqh_texts_leaf.json", "sharia_sources_leaf.json"]
                        }
                    },
                    "judaism": {
                        "limbs": {
                            "hebrew_scriptures": ["tanakh_leaf.json", "talmud_leaf.json"],
                            "rabbinical_literature": ["midrash_leaf.json", "responsa_leaf.json"],
                            "mystical_texts": ["kabbalah_leaf.json", "zohar_leaf.json"]
                        }
                    },
                    "hinduism": {
                        "limbs": {
                            "vedic_texts": ["vedas_leaf.json", "upanishads_leaf.json"],
                            "epic_literature": ["mahabharata_leaf.json", "ramayana_leaf.json"],
                            "philosophical_texts": ["bhagavad_gita_leaf.json", "vedanta_texts_leaf.json"]
                        }
                    },
                    "buddhism": {
                        "limbs": {
                            "canonical_texts": ["tripitaka_leaf.json", "sutras_leaf.json"],
                            "commentaries": ["abhidhamma_leaf.json", "scholastic_texts_leaf.json"],
                            "meditation_texts": ["zen_literature_leaf.json", "vipassana_texts_leaf.json"]
                        }
                    }
                }
            },
            "science": {
                "tree_file": "science_tree.json",
                "branches": {
                    "physics": {
                        "limbs": {
                            "classical_physics": ["newton_principia_leaf.json", "maxwell_equations_leaf.json"],
                            "quantum_mechanics": ["heisenberg_papers_leaf.json", "schrodinger_papers_leaf.json"],
                            "relativity": ["einstein_papers_leaf.json", "spacetime_texts_leaf.json"]
                        }
                    },
                    "mathematics": {
                        "limbs": {
                            "pure_mathematics": ["euclid_elements_leaf.json", "number_theory_texts_leaf.json"],
                            "applied_mathematics": ["calculus_texts_leaf.json", "statistics_texts_leaf.json"],
                            "modern_mathematics": ["abstract_algebra_leaf.json", "topology_texts_leaf.json"]
                        }
                    },
                    "computer_science": {
                        "limbs": {
                            "theoretical_cs": ["algorithms_texts_leaf.json", "complexity_theory_leaf.json"],
                            "programming": ["language_design_leaf.json", "software_engineering_leaf.json"],
                            "artificial_intelligence": ["machine_learning_texts_leaf.json", "cognitive_science_leaf.json"]
                        }
                    }
                }
            },
            "history": {
                "tree_file": "history_tree.json",
                "branches": {
                    "ancient_history": {
                        "limbs": {
                            "mesopotamia": ["sumerian_texts_leaf.json", "babylonian_records_leaf.json"],
                            "egypt": ["hieroglyphic_texts_leaf.json", "papyrus_collections_leaf.json"],
                            "classical_antiquity": ["herodotus_histories_leaf.json", "thucydides_leaf.json"]
                        }
                    },
                    "medieval_history": {
                        "limbs": {
                            "early_medieval": ["chroniclers_leaf.json", "monastic_records_leaf.json"],
                            "high_medieval": ["crusade_chronicles_leaf.json", "scholastic_records_leaf.json"],
                            "late_medieval": ["renaissance_precursors_leaf.json"]
                        }
                    },
                    "modern_history": {
                        "limbs": {
                            "renaissance": ["humanism_texts_leaf.json", "reformation_documents_leaf.json"],
                            "enlightenment": ["philosophes_works_leaf.json", "scientific_revolution_leaf.json"],
                            "industrial_age": ["social_changes_leaf.json", "technological_advances_leaf.json"]
                        }
                    }
                }
            }
        }
    
    def reorganize_structure(self):
        """Reorganize the entire forest structure"""
        ideal_structure = self.get_ideal_structure()
        
        for tree_name, tree_config in ideal_structure.items():
            tree_path = self.root_path / tree_name
            
            # Create tree directory if it doesn't exist
            tree_path.mkdir(exist_ok=True)
            
            # Ensure tree file exists
            tree_file_path = tree_path / tree_config["tree_file"]
            if not tree_file_path.exists():
                self.create_tree_file(tree_file_path, tree_name)
            
            # Create branches directory
            branches_path = tree_path / "branches"
            branches_path.mkdir(exist_ok=True)
            
            # Create each branch
            for branch_name, branch_config in tree_config["branches"].items():
                branch_path = branches_path / branch_name
                branch_path.mkdir(exist_ok=True)
                
                # Create limbs within each branch
                for limb_name, leaf_files in branch_config["limbs"].items():
                    limb_path = branch_path / limb_name
                    limb_path.mkdir(exist_ok=True)
                    
                    # Create leaf files within each limb
                    for leaf_file in leaf_files:
                        leaf_path = limb_path / leaf_file
                        if not leaf_path.exists():
                            self.create_sample_leaf_file(leaf_path, tree_name, branch_name, limb_name)
        
        print("Forest structure reorganized successfully!")
    
    def create_tree_file(self, file_path, tree_name):
        """Create a tree JSON file"""
        tree_data = {
            "tree_name": tree_name.replace("_", " ").title(),
            "description": f"Main knowledge tree for {tree_name}",
            "branches": [],
            "metadata": {
                "created": "2025-06-22",
                "structure_version": "1.0",
                "total_branches": 0
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tree_data, f, indent=2, ensure_ascii=False)
        
        print(f"Created tree file: {file_path}")
    
    def create_sample_leaf_file(self, file_path, tree_name, branch_name, limb_name):
        """Create a sample leaf file with proper structure"""
        leaf_name = file_path.stem.replace("_leaf", "").replace("_", " ").title()
        
        leaf_data = {
            "limb": limb_name.replace("_", " ").title(),
            "leaf_name": leaf_name,
            "leaf_type": "text_collection",
            "tree_path": f"{tree_name.title()} → {branch_name.replace('_', ' ').title()} → {limb_name.replace('_', ' ').title()} → {leaf_name}",
            "resources": [
                {
                    "title": f"Sample {leaf_name} Resource",
                    "author": "Unknown",
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
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(leaf_data, f, indent=2, ensure_ascii=False)
        
        print(f"Created leaf file: {file_path}")
    
    def clean_old_files(self):
        """Remove old files that don't fit the new structure"""
        old_files = [
            "antiquity.json",
            "psychology.json", 
            "quantum_com.json",
            "quantum_mech.json",
            "quantum_phys.json",
            "language_tree.json"
        ]
        
        for old_file in old_files:
            old_path = self.root_path / old_file
            if old_path.exists():
                # Move to backup instead of deleting
                backup_file_path = self.backup_path / old_file
                if not backup_file_path.exists():
                    shutil.move(str(old_path), str(backup_file_path))
                    print(f"Moved old file to backup: {old_file}")
    
    def generate_master_structure_file(self):
        """Generate updated master structure file"""
        master_structure = {
            "forest_name": "S.IO Knowledge Forest",
            "version": "2.0",
            "restructure_date": "2025-06-22",
            "structure_type": "Tree→Branches→Limbs→Leafs",
            "trees": {}
        }
        
        # Scan actual structure and populate master file
        for tree_dir in self.root_path.iterdir():
            if tree_dir.is_dir() and tree_dir.name not in ['backup_before_reorganization', '__pycache__']:
                if (tree_dir / "branches").exists():
                    master_structure["trees"][tree_dir.name] = self.scan_tree_structure(tree_dir)
        
        master_file = self.root_path / "master_tree_structure.json"
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(master_structure, f, indent=2, ensure_ascii=False)
        
        print(f"Generated master structure file: {master_file}")
    
    def scan_tree_structure(self, tree_path):
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
                            structure["branches"][branch_dir.name]["limbs"][limb_dir.name] = limb_leafs
        
        return structure
    
    def run_full_reorganization(self):
        """Run the complete reorganization process"""
        print("Starting S.IO Forest Reorganization...")
        print("=" * 50)
        
        # Step 1: Create backup
        self.create_backup()
        
        # Step 2: Reorganize structure
        self.reorganize_structure()
        
        # Step 3: Clean old files
        self.clean_old_files()
        
        # Step 4: Generate master structure
        self.generate_master_structure_file()
        
        print("=" * 50)
        print("Reorganization complete!")
        print(f"Backup available at: {self.backup_path}")
        print("\nNew structure follows: Tree→Branches→Limbs→Leafs")
        print("- Trees: Main knowledge domains")
        print("- Branches: Major subdivisions")  
        print("- Limbs: Specific categories")
        print("- Leafs: Individual resources/texts")

if __name__ == "__main__":
    root_path = "/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json"
    reorganizer = ForestReorganizer(root_path)
    reorganizer.run_full_reorganization()
