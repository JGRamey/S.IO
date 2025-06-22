#!/usr/bin/env python3
"""
Migration Script: JSON Files → Database
Helps transition from static JSON files to database-driven approach
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime

def analyze_current_structure():
    """Analyze what we have vs what we need"""
    
    root = Path("/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json")
    
    print("🔍 ANALYZING CURRENT SITUATION")
    print("=" * 50)
    
    # Count current files
    total_json_files = 0
    total_size = 0
    
    for json_file in root.rglob("*.json"):
        if "database_schema" not in str(json_file):
            total_json_files += 1
            total_size += json_file.stat().st_size
    
    print(f"📁 Static JSON files: {total_json_files}")
    print(f"💾 Total size: {total_size / 1024:.1f} KB")
    
    # Check database readiness
    db_schema_path = root / "database_schema"
    if db_schema_path.exists():
        print("✅ Database schema files ready")
        
        schema_files = list(db_schema_path.glob("*.sql"))
        model_files = list(db_schema_path.glob("*.py"))
        
        print(f"📊 Schema files: {len(schema_files)}")
        print(f"🐍 Python model files: {len(model_files)}")
    else:
        print("❌ Database schema not found")
    
    return total_json_files, total_size

def create_transition_plan():
    """Create a step-by-step transition plan"""
    
    plan = """
# 🚀 TRANSITION PLAN: JSON Files → Database

## Phase 1: Database Setup
1. Create PostgreSQL database named 'yggdrasil'
2. Run `database_schema/schema.sql` to create tables
3. Run `database_schema/initial_migration.sql` to populate structure
4. Test database connection

## Phase 2: Web Scraper Integration  
1. Install SQLAlchemy: `pip install sqlalchemy psycopg2-binary`
2. Use `database_schema/models.py` in your scraper
3. Use `database_schema/api_example.py` as reference
4. Point scraper to populate `resources` table directly

## Phase 3: Verify & Clean Up
1. Verify all scraped data is in database
2. Test search and query functionality
3. Archive static JSON files
4. Update any existing code to use database

## Code Changes Needed
- Replace file system traversal with SQL queries
- Use database connection instead of JSON file reading
- Implement full-text search using PostgreSQL
- Add proper error handling and transactions

## Benefits After Migration
✅ Single source of truth (database)
✅ Powerful search capabilities  
✅ Automatic relationship tracking
✅ Better performance at scale
✅ ACID compliance
✅ Concurrent access support
✅ Backup and recovery built-in
"""
    
    return plan

def create_archive():
    """Archive current JSON structure for backup"""
    
    root = Path("/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = root / f"archive_json_structure_{timestamp}"
    
    print(f"\n📦 Creating archive: {archive_path.name}")
    
    # Create archive directory
    archive_path.mkdir(exist_ok=True)
    
    # Copy all JSON tree structures
    trees_to_archive = ["philosophy", "religion", "science", "history", "astrology"]
    
    for tree_name in trees_to_archive:
        tree_path = root / tree_name
        if tree_path.exists():
            archive_tree_path = archive_path / tree_name
            shutil.copytree(tree_path, archive_tree_path)
            print(f"📁 Archived: {tree_name}")
    
    # Copy important files
    important_files = [
        "master_tree_structure.json",
        "README.md",
        "forest_structure_guide.md"
    ]
    
    for file_name in important_files:
        file_path = root / file_name
        if file_path.exists():
            shutil.copy2(file_path, archive_path / file_name)
            print(f"📄 Archived: {file_name}")
    
    # Create archive README
    archive_readme = f"""# Archived JSON Structure - {timestamp}

This archive contains the original static JSON file structure before migration to database.

## Contents
- Tree directories with full Branch→Limb→Leaf structure
- Master structure files
- Documentation

## Purpose
- Backup before database migration
- Reference for structure validation
- Rollback capability if needed

Archived on: {datetime.now().isoformat()}
"""
    
    with open(archive_path / "ARCHIVE_README.md", 'w') as f:
        f.write(archive_readme)
    
    print(f"✅ Archive created: {archive_path}")
    return archive_path

def show_database_commands():
    """Show the database setup commands"""
    
    commands = """
# 🗄️ DATABASE SETUP COMMANDS

## 1. Create PostgreSQL Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE yggdrasil;
CREATE USER yggdrasil_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE yggdrasil TO yggdrasil_user;
\\q
```

## 2. Initialize Schema
```bash
# Run schema creation
psql -U yggdrasil_user -d yggdrasil -f database_schema/schema.sql

# Populate initial structure  
psql -U yggdrasil_user -d yggdrasil -f database_schema/initial_migration.sql
```

## 3. Test Connection
```python
from database_schema.api_example import YggdrasilAPI

# Update connection string with your credentials
api = YggdrasilAPI("postgresql://yggdrasil_user:your_password@localhost/yggdrasil")

# Test
structure = api.get_tree_structure("philosophy")
print(structure)
```

## 4. Integration Example
```python
# In your web scraper
from database_schema.api_example import YggdrasilAPI

api = YggdrasilAPI("postgresql://yggdrasil_user:your_password@localhost/yggdrasil")

# Add scraped content
api.add_scraped_resource(
    tree_name="philosophy",
    branch_name="ancient_philosophy", 
    limb_name="greek_philosophy",
    title="The Republic",
    author="Plato",
    content="scraped_content_here...",
    source_url="https://example.com/republic"
)
```
"""
    
    return commands

def main():
    """Main migration analysis and planning"""
    
    print("🌲 YGGDRASIL MIGRATION ANALYZER")
    print("=" * 50)
    
    # Analyze current situation
    file_count, total_size = analyze_current_structure()
    
    # Show transition plan
    plan = create_transition_plan()
    print(plan)
    
    # Show database commands
    commands = show_database_commands()
    print(commands)
    
    # Offer to create archive
    response = input("\n📦 Create archive of current JSON structure? (y/n): ").lower()
    if response == 'y':
        archive_path = create_archive()
        print(f"\n✅ Archive created: {archive_path}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Set up PostgreSQL database")
    print("2. Run database schema files") 
    print("3. Update web scraper to use database API")
    print("4. Test with sample data")
    print("5. Archive static JSON files")
    
    print(f"\n💡 TIP: The database approach will be much more efficient")
    print(f"   for {file_count} files and growing!")

if __name__ == "__main__":
    main()
