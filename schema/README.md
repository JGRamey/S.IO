# S.IO Knowledge Forest Database Schema

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
