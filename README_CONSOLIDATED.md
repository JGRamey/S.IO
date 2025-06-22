# S.IO Knowledge Database - Consolidated

Clean, simplified project structure for the S.IO knowledge database.

## Directory Structure

- `schema/` - Database schema and models
- `tools/` - Simple utility scripts  
- `archive/` - Archived original files
- `solomon/` - Main application code

## Quick Start

1. **Setup Database**
   ```bash
   createdb yggdrasil
   psql yggdrasil < schema/schema.sql
   psql yggdrasil < schema/initial_migration.sql
   ```

2. **Use Database API**
   ```python
   from schema.api_example import YggdrasilAPI
   
   api = YggdrasilAPI("postgresql://localhost/yggdrasil")
   api.add_scraped_resource(...)
   ```

3. **Use Tools**
   ```bash
   python tools/tools.py structure
   python tools/tools.py validate
   ```

## Benefits

- Reduced from 245+ files to ~10 essential files
- Database-driven (no static JSON files)
- Clear separation of concerns
- All functionality preserved

## Original Structure

The original yggdrasil.json directory with 245+ files has been archived.
The knowledge structure (Tree→Branch→Limb→Resource) is now defined in the database schema.
