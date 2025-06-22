#!/usr/bin/env python3
"""
Convert Yggdrasil Structure to Database Schema
Transforms the file structure into database table definitions and migration scripts
"""

import json
import os
from pathlib import Path

def generate_database_schema():
    """Generate SQL schema from the forest structure"""
    
    schema_sql = """
-- S.IO Knowledge Forest Database Schema
-- Generated from yggdrasil.json structure
-- Date: 2025-06-22

-- Main trees table
CREATE TABLE trees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Branches table  
CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    tree_id INTEGER REFERENCES trees(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tree_id, name)
);

-- Limbs table
CREATE TABLE limbs (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES branches(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(branch_id, name)
);

-- Resources table (the actual content/leafs)
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    limb_id INTEGER REFERENCES limbs(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(200),
    category VARCHAR(100),
    description TEXT,
    content TEXT, -- For scraped content
    source_url VARCHAR(1000), -- Original URL if scraped
    key_concepts JSONB, -- Store as JSON array
    metadata JSONB, -- Additional flexible metadata
    tree_path VARCHAR(1000), -- Computed path for easy navigation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scraped_at TIMESTAMP -- When it was last scraped
);

-- Cross-references table for related resources
CREATE TABLE resource_cross_references (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    related_resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50), -- 'related', 'cited_by', 'influences', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resource_id, related_resource_id, relationship_type)
);

-- Indexes for performance
CREATE INDEX idx_resources_limb_id ON resources(limb_id);
CREATE INDEX idx_resources_title ON resources USING GIN (to_tsvector('english', title));
CREATE INDEX idx_resources_content ON resources USING GIN (to_tsvector('english', content));
CREATE INDEX idx_resources_key_concepts ON resources USING GIN (key_concepts);
CREATE INDEX idx_resources_tree_path ON resources(tree_path);
CREATE INDEX idx_resources_scraped_at ON resources(scraped_at);

-- Views for easy querying
CREATE VIEW resource_full_path AS
SELECT 
    r.id,
    r.title,
    r.author,
    t.name as tree_name,
    b.name as branch_name,
    l.name as limb_name,
    r.tree_path,
    r.created_at
FROM resources r
JOIN limbs l ON r.limb_id = l.id
JOIN branches b ON l.branch_id = b.id  
JOIN trees t ON b.tree_id = t.id;

-- Function to update tree_path automatically
CREATE OR REPLACE FUNCTION update_resource_tree_path()
RETURNS TRIGGER AS $$
BEGIN
    SELECT 
        t.name || ' → ' || b.name || ' → ' || l.name || ' → ' || NEW.title
    INTO NEW.tree_path
    FROM limbs l
    JOIN branches b ON l.branch_id = b.id
    JOIN trees t ON b.tree_id = t.id
    WHERE l.id = NEW.limb_id;
    
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update tree_path
CREATE TRIGGER trigger_update_resource_tree_path
    BEFORE INSERT OR UPDATE ON resources
    FOR EACH ROW
    EXECUTE FUNCTION update_resource_tree_path();
"""

    return schema_sql

def generate_data_migration():
    """Generate migration script to populate initial structure"""
    
    root = Path("/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json")
    
    migration_sql = """
-- S.IO Forest Structure Data Migration  
-- Populates initial tree/branch/limb structure
-- Date: 2025-06-22

"""
    
    # Scan current structure and generate INSERT statements
    trees = [d for d in root.iterdir() if d.is_dir() and (d / "branches").exists()]
    
    tree_inserts = []
    branch_inserts = []
    limb_inserts = []
    
    for tree_dir in sorted(trees):
        tree_name = tree_dir.name
        tree_inserts.append(f"INSERT INTO trees (name, description) VALUES ('{tree_name}', 'Knowledge domain for {tree_name}');")
        
        branches_dir = tree_dir / "branches"
        if branches_dir.exists():
            branches = [d for d in branches_dir.iterdir() if d.is_dir()]
            
            for branch_dir in sorted(branches):
                branch_name = branch_dir.name
                branch_inserts.append(
                    f"INSERT INTO branches (tree_id, name, description) "
                    f"SELECT id, '{branch_name}', 'Branch for {branch_name.replace('_', ' ')}' "
                    f"FROM trees WHERE name = '{tree_name}';"
                )
                
                limbs = [d for d in branch_dir.iterdir() if d.is_dir()]
                for limb_dir in sorted(limbs):
                    limb_name = limb_dir.name
                    limb_inserts.append(
                        f"INSERT INTO limbs (branch_id, name, description) "
                        f"SELECT b.id, '{limb_name}', 'Category for {limb_name.replace('_', ' ')}' "
                        f"FROM branches b JOIN trees t ON b.tree_id = t.id "
                        f"WHERE t.name = '{tree_name}' AND b.name = '{branch_name}';"
                    )
    
    migration_sql += "-- Insert Trees\n"
    migration_sql += "\n".join(tree_inserts)
    migration_sql += "\n\n-- Insert Branches\n"
    migration_sql += "\n".join(branch_inserts)
    migration_sql += "\n\n-- Insert Limbs\n"
    migration_sql += "\n".join(limb_inserts)
    
    return migration_sql

def generate_api_models():
    """Generate Python data models for the API"""
    
    models_code = '''"""
S.IO Knowledge Forest Data Models
SQLAlchemy models for the forest database
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Tree(Base):
    __tablename__ = 'trees'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    branches = relationship("Branch", back_populates="tree", cascade="all, delete-orphan")

class Branch(Base):
    __tablename__ = 'branches'
    
    id = Column(Integer, primary_key=True)
    tree_id = Column(Integer, ForeignKey('trees.id'))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    tree = relationship("Tree", back_populates="branches")
    limbs = relationship("Limb", back_populates="branch", cascade="all, delete-orphan")

class Limb(Base):
    __tablename__ = 'limbs'
    
    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey('branches.id'))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    branch = relationship("Branch", back_populates="limbs")
    resources = relationship("Resource", back_populates="limb", cascade="all, delete-orphan")

class Resource(Base):
    __tablename__ = 'resources'
    
    id = Column(Integer, primary_key=True)
    limb_id = Column(Integer, ForeignKey('limbs.id'))
    title = Column(String(500), nullable=False)
    author = Column(String(200))
    category = Column(String(100))
    description = Column(Text)
    content = Column(Text)  # Scraped content
    source_url = Column(String(1000))  # Original URL
    key_concepts = Column(JSON)  # Store as JSON array
    metadata = Column(JSON)  # Additional metadata
    tree_path = Column(String(1000))  # Auto-computed path
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    scraped_at = Column(DateTime)  # Last scraped timestamp
    
    limb = relationship("Limb", back_populates="resources")
    cross_references = relationship("ResourceCrossReference", 
                                  foreign_keys="ResourceCrossReference.resource_id",
                                  back_populates="resource")

class ResourceCrossReference(Base):
    __tablename__ = 'resource_cross_references'
    
    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('resources.id'))
    related_resource_id = Column(Integer, ForeignKey('resources.id'))
    relationship_type = Column(String(50))  # 'related', 'cited_by', etc.
    created_at = Column(DateTime, default=func.now())
    
    resource = relationship("Resource", foreign_keys=[resource_id])
    related_resource = relationship("Resource", foreign_keys=[related_resource_id])
'''
    
    return models_code

def create_database_files():
    """Create all database-related files"""
    
    root = Path("/Users/grant/Desktop/Solomon/Backend:Database/S.IO/yggdrasil.json")
    db_dir = root / "database_schema"
    db_dir.mkdir(exist_ok=True)
    
    # Generate schema
    schema_sql = generate_database_schema()
    with open(db_dir / "schema.sql", 'w') as f:
        f.write(schema_sql)
    
    # Generate migration
    migration_sql = generate_data_migration()
    with open(db_dir / "initial_migration.sql", 'w') as f:
        f.write(migration_sql)
    
    # Generate models
    models_code = generate_api_models()
    with open(db_dir / "models.py", 'w') as f:
        f.write(models_code)
    
    # Generate README
    readme_content = """# S.IO Knowledge Forest Database Schema

This directory contains the database schema and related files for the S.IO Knowledge Forest.

## Files

- `schema.sql` - Complete database schema with tables, indexes, and triggers
- `initial_migration.sql` - Migration script to populate initial tree/branch/limb structure  
- `models.py` - SQLAlchemy models for Python applications
- `api_example.py` - Example API usage with the models

## Usage

1. Create database and run schema.sql
2. Run initial_migration.sql to populate structure
3. Use models.py in your Python applications
4. Web scraper can now populate the `resources` table directly

## Benefits of Database Approach

- ✅ Single source of truth
- ✅ Powerful querying capabilities  
- ✅ Full-text search on content
- ✅ Automatic tree path computation
- ✅ Cross-reference tracking
- ✅ Scalable for large datasets
- ✅ Built-in timestamp tracking
- ✅ ACID compliance
"""
    
    with open(db_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"📊 Created database schema files in: {db_dir}")
    print("✅ Generated:")
    print("  - schema.sql (complete database schema)")
    print("  - initial_migration.sql (structure population)")  
    print("  - models.py (SQLAlchemy models)")
    print("  - README.md (usage documentation)")

if __name__ == "__main__":
    create_database_files()
    
    print("\n🎯 RECOMMENDATION:")
    print("=" * 50)
    print("1. Use database_schema/ files as your source of truth")
    print("2. Archive or delete the static JSON files")
    print("3. Point your web scraper to populate the 'resources' table")
    print("4. Use SQL queries instead of file system traversal")
    print("5. Maintain the Tree→Branch→Limb→Resource hierarchy in the database")
