# Subfields.json Restructure Plan

## Problem
Current structure is inconsistent:
- Files named like subfields (religion.json) actually contain FIELD definitions
- Each file duplicates the field-subfield relationship structure
- This contradicts the database schema and causes confusion

## Current Structure (BROKEN)
```
subfields.json/
├── religion.json     # Contains: "field": "Religious Books..." + subfields array
├── philosophy.json   # Contains: "field": "Philosophical Books..." + subfields array
├── math.json        # Contains: "field": "Mathematical Books..." + subfields array
└── ...
```

## Proposed Structure (FIXED)
```
subfields.json/
├── fields.json       # Master list of all fields
└── subfields/
    ├── religion/
    │   ├── christianity.json
    │   ├── islam.json
    │   ├── buddhism.json
    │   └── ...
    ├── philosophy/
    │   ├── ancient_philosophy.json
    │   ├── medieval_philosophy.json
    │   └── ...
    └── math/
        ├── algebra.json
        ├── geometry.json
        └── ...
```

## Alternative Structure (SIMPLER)
```
subfields.json/
├── master_taxonomy.json  # Complete hierarchical structure
└── individual_files/     # Optional: separate files for large categories
    ├── religion_subfields.json
    ├── philosophy_subfields.json
    └── ...
```

## Benefits of Restructure
1. **Matches Database Schema**: Aligns with field_categories → subfield_categories
2. **Eliminates Redundancy**: No duplicate field definitions
3. **Scalable**: Easy to add new subfields without modifying multiple files
4. **Clear Hierarchy**: Field → Subfield relationship is obvious
5. **Consistent Naming**: File structure matches content structure

## Implementation Steps
1. Create new structure
2. Migrate existing data
3. Update populate_categories.py script
4. Update any code that reads subfields.json
5. Delete old inconsistent files
