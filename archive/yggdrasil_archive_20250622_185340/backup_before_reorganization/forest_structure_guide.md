# S.IO Knowledge Forest Structure Guide

## Tree Metaphor System

The S.IO knowledge database uses a natural tree metaphor for organization:

- **🌳 Trees**: Main knowledge domains (Philosophy, Religion, Science, etc.)
- **🌿 Branches**: Major subdivisions within each tree
- **🌱 Limbs**: Specific categories within branches
- **🍃 Leafs**: Individual resources/files within limbs

## Directory Structure

```
trees.json/
├── master_tree_structure.json          # Complete hierarchical overview
├── forest_structure_guide.md           # This guide
├── branches.json/                       # Branch definitions
│   ├── philosophy_branches.json
│   ├── religion_branches.json
│   ├── science_branches.json
│   └── limbs.json/                     # Limb directories
│       ├── philosophy/
│       │   ├── ancient_philosophy/
│       │   │   ├── greek_philosophy/
│       │   │   │   ├── plato_works_leaf.json
│       │   │   │   ├── aristotle_works_leaf.json
│       │   │   │   └── socratic_dialogues_leaf.json
│       │   │   └── roman_philosophy/
│       │   ├── medieval_philosophy/
│       │   └── ethics_and_moral_philosophy/
│       ├── religion/
│       │   ├── christianity/
│       │   │   ├── biblical_texts/
│       │   │   │   ├── old_testament_leaf.json
│       │   │   │   ├── new_testament_leaf.json
│       │   │   │   └── apocrypha_leaf.json
│       │   │   ├── protestant_denominations/
│       │   │   └── catholic_doctrine/
│       │   ├── islam/
│       │   └── buddhism/
│       └── science/
│           ├── physics/
│           ├── mathematics/
│           └── computer_science/
└── [legacy files to be restructured]
```

## Naming Convention

### Trees
- Format: `{domain}_tree` (e.g., `philosophy_tree`, `religion_tree`)
- Files: `{domain}.json` (main tree definition)
- Branch files: `{domain}_branches.json`

### Branches
- Format: `{subdivision}` (e.g., `ancient_philosophy`, `christianity`)
- Directory: `branches.json/{domain}_branches.json`

### Limbs
- Format: `{specific_category}` (e.g., `greek_philosophy`, `biblical_texts`)
- Directory: `limbs.json/{domain}/{branch}/{limb}/`

### Leafs
- Format: `{resource_name}_leaf.json` (e.g., `plato_works_leaf.json`)
- Location: `limbs.json/{domain}/{branch}/{limb}/{leaf_name}_leaf.json`

## Leaf File Structure

Each leaf file contains:
- **limb**: Parent limb name
- **leaf_name**: Display name
- **leaf_type**: Category type
- **tree_path**: Full hierarchical path
- **resources**: Array of individual resources
- **metadata**: Additional information and cross-references

## Usage Examples

### Philosophy Tree Path
```
Philosophy-Tree → Ancient Philosophy → Greek Philosophy → Plato Works
```

### Religion Tree Path  
```
Religion-Tree → Christianity → Biblical Texts → New Testament
```

### Science Tree Path
```
Science-Tree → Physics → Quantum Mechanics → Wave Particle Duality
```

## Migration Strategy

1. **Identify** existing content in legacy files
2. **Categorize** into appropriate tree/branch/limb structure
3. **Create** leaf files with proper metadata
4. **Cross-reference** related content across trees
5. **Update** database schema to reflect new structure

## Benefits

- **Hierarchical Organization**: Clear parent-child relationships
- **Scalability**: Easy to add new branches and limbs
- **Cross-referencing**: Metadata enables connections between trees
- **Intuitive Navigation**: Natural metaphor for knowledge exploration
- **Modular Structure**: Individual components can be updated independently

## Next Steps

1. Complete migration of existing content
2. Populate remaining branch/limb structures
3. Implement database integration
4. Create search and navigation interfaces
5. Add content validation and quality checks
