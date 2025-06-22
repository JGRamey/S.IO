# S.IO Knowledge Forest 🌲

## Overview

The S.IO Knowledge Forest is a comprehensive, hierarchically organized database of human knowledge using a natural tree metaphor for intuitive navigation and understanding.

## 🏗️ Structure

The forest follows the **Tree → Branches → Limbs → Leafs** pattern:

- **🌳 Trees**: Main knowledge domains (Philosophy, Religion, Science, History)
- **🌿 Branches**: Major subdivisions within each tree
- **🌱 Limbs**: Specific categories within branches  
- **🍃 Leafs**: Individual resources/texts/manuscripts (the actual data sources)

## 📊 Current Statistics

- **7 Trees**: Main knowledge domains
- **35 Branches**: Major subdivisions
- **70 Limbs**: Specific categories
- **145 Leafs**: Individual books/texts/manuscripts

## 🌳 Available Trees

### Philosophy Tree
- **Ancient Philosophy**: Greek, Roman, Hellenistic traditions
- **Medieval Philosophy**: Scholasticism, Islamic, Jewish philosophy  
- **Modern Philosophy**: Rationalism, Empiricism, German Idealism
- **Contemporary Philosophy**: Analytic, Continental, Existentialism

### Religion Tree  
- **Christianity**: Biblical texts, Patristic literature, Denominational texts
- **Islam**: Islamic texts, Philosophy, Jurisprudence
- **Judaism**: Hebrew scriptures, Rabbinical literature, Mystical texts
- **Hinduism**: Vedic texts, Epic literature, Philosophical texts
- **Buddhism**: Canonical texts, Commentaries, Meditation texts

### Science Tree
- **Physics**: Classical, Quantum mechanics, Relativity
- **Mathematics**: Pure, Applied, Modern mathematics
- **Computer Science**: Theoretical CS, Programming, AI

### History Tree
- **Ancient History**: Mesopotamia, Egypt, Classical antiquity
- **Medieval History**: Early, High, Late medieval periods
- **Modern History**: Renaissance, Enlightenment, Industrial age

### Astrology Tree
- **Western Astrology**: Classical, Modern, Horary traditions
- **Vedic Astrology**: Classical texts, Computational methods, Predictive techniques
- **Chinese Astrology**: Classical systems, Feng Shui, Traditional texts
- **Natal Astrology**: Chart interpretation, House systems, Timing techniques
- **Mundane Astrology**: Political, Economic, Natural disaster prediction
- **Esoteric Astrology**: Soul, Karmic, Hermetic traditions

## 📁 Directory Structure

```
yggdrasil.json/
├── [tree_name]/
│   ├── [tree_name]_tree.json          # Tree metadata
│   └── branches/
│       └── [branch_name]/
│           └── [limb_name]/
│               └── [resource]_leaf.json    # Individual resources
```

## 🍃 Leaf File Format

Each leaf file follows this standardized JSON structure:

```json
{
  "limb": "Category Name",
  "leaf_name": "Resource Name",
  "leaf_type": "text_collection|sacred_scripture|philosophical_texts|etc",
  "tree_path": "Tree → Branch → Limb → Leaf",
  "resources": [
    {
      "title": "Resource Title",
      "author": "Author Name",
      "category": "subcategory",
      "description": "Brief description",
      "key_concepts": ["concept1", "concept2", "concept3"]
    }
  ],
  "metadata": {
    "total_resources": 0,
    "primary_themes": ["theme1", "theme2"],
    "related_limbs": ["related_limb1", "related_limb2"],
    "cross_references": ["reference1", "reference2"]
  }
}
```

## 🛠️ Management Tools

- **`show_structure.py`**: Visualize the complete forest structure
- **`reorganize_forest.py`**: Restructure and organize the database
- **`cleanup_legacy.py`**: Clean up legacy files and enhance content
- **`master_tree_structure.json`**: Complete hierarchical overview

## 🗂️ File Organization

### Core Files
- `README.md` - This documentation
- `forest_structure_guide.md` - Detailed structure guide
- `master_tree_structure.json` - Complete hierarchy map

### Archive
- `backup_before_reorganization/` - Original files before restructuring
- `archive_legacy_files/` - Cleaned up legacy files

### Trees
Each tree has its own directory with:
- `[tree_name]_tree.json` - Tree metadata and overview
- `branches/` - All branches for that tree

## 🚀 Usage

### Viewing Structure
```bash
python3 show_structure.py
```

### Adding New Content
1. Navigate to appropriate Tree → Branch → Limb
2. Create new `[name]_leaf.json` file
3. Follow the standard leaf file format
4. Update related cross-references

### Finding Resources
Resources are organized by:
- **Domain** (Tree level)
- **Field** (Branch level) 
- **Specialization** (Limb level)
- **Individual texts** (Leaf level)

## 🔗 Cross-References

The system supports cross-references between:
- Related limbs within the same tree
- Related concepts across different trees
- Historical connections and influences
- Thematic relationships

## 📈 Future Expansion

The structure is designed to accommodate:
- **Sub-trees**: For highly complex domains
- **Sub-branches**: For detailed specializations
- **Additional trees**: New knowledge domains
- **Enhanced metadata**: Richer resource descriptions

## 🎯 Design Principles

1. **Natural Metaphor**: Tree structure mirrors organic growth
2. **Scalability**: Can expand without restructuring
3. **Consistency**: Uniform format across all resources
4. **Discoverability**: Intuitive navigation paths
5. **Interconnection**: Rich cross-referencing system

---

*The S.IO Knowledge Forest grows with human understanding, branching naturally as knowledge expands and deepens.*
