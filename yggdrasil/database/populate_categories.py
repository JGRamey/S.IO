"""Script to populate field_categories and subfield_categories tables from subfields.json directory."""

import json
import asyncio
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from sqlalchemy import select
from yggdrasil.database.connection import db_manager
from yggdrasil.database.models import FieldCategory, SubfieldCategory


class CategoryPopulator:
    """Populates database categories from subfields.json directory."""
    
    def __init__(self):
        self.subfields_dir = Path("subfields.json")
        self.fields_data = {}
        
    def load_1fields_data(self) -> Dict[str, Any]:
        """Load and parse the 1fields.md file to extract field structure."""
        fields_file = self.subfields_dir / "1fields.md"
        
        if not fields_file.exists():
            raise FileNotFoundError(f"1fields.md not found in {self.subfields_dir}")
        
        # Read the file and extract JSON content
        content = fields_file.read_text(encoding='utf-8')
        
        # Find the JSON section in the markdown file
        json_start = content.find('{\n  "fields":')
        json_end = content.rfind('}') + 1
        
        if json_start == -1 or json_end == -1:
            raise ValueError("Could not find JSON structure in 1fields.md")
        
        json_content = content[json_start:json_end]
        
        try:
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in 1fields.md: {e}")
    
    def load_individual_json_files(self) -> Dict[str, Dict[str, Any]]:
        """Load individual JSON files from subfields.json directory."""
        json_files = {}
        
        for json_file in self.subfields_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    json_files[json_file.stem] = data
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load {json_file}: {e}")
                continue
        
        return json_files
    
    def merge_field_data(self) -> Dict[str, Dict[str, Any]]:
        """Merge data from 1fields.md and individual JSON files."""
        # Load main structure from 1fields.md
        try:
            main_data = self.load_1fields_data()
            fields_dict = {}
            
            # Convert to dictionary format
            for field_data in main_data.get("fields", []):
                field_name = field_data.get("field", "")
                subfields = field_data.get("subfields", [])
                
                fields_dict[field_name] = {
                    "field": field_name,
                    "subfields": subfields,
                    "description": f"Field containing {len(subfields)} subfields"
                }
            
            # Load individual JSON files for additional details
            json_files = self.load_individual_json_files()
            
            # Merge additional data from individual JSON files
            for filename, json_data in json_files.items():
                field_name = json_data.get("field", "")
                if field_name and field_name in fields_dict:
                    # Update with more detailed information if available
                    fields_dict[field_name].update(json_data)
                elif field_name:
                    # Add new field from individual JSON file
                    fields_dict[field_name] = json_data
            
            return fields_dict
            
        except Exception as e:
            print(f"Error loading 1fields.md, falling back to individual JSON files: {e}")
            # Fallback to individual JSON files only
            return self.load_individual_json_files()
    
    async def populate_database(self):
        """Populate the database with field and subfield categories."""
        print("Loading field and subfield data...")
        self.fields_data = self.merge_field_data()
        
        print(f"Found {len(self.fields_data)} fields to process")
        
        async with db_manager.get_async_session() as session:
            # Clear existing data (optional - remove if you want to preserve existing data)
            # await session.execute("DELETE FROM subfield_categories")
            # await session.execute("DELETE FROM field_categories")
            
            field_count = 0
            subfield_count = 0
            
            for field_name, field_data in self.fields_data.items():
                # Check if field already exists
                existing_field = await session.execute(
                    select(FieldCategory).where(FieldCategory.field_name == field_name)
                )
                field_category = existing_field.scalar_one_or_none()
                
                if not field_category:
                    # Create new field category
                    field_category = FieldCategory(
                        id=str(uuid.uuid4()),
                        field_name=field_name,
                        description=field_data.get("description", f"Field: {field_name}"),
                        created_at=datetime.utcnow()
                    )
                    session.add(field_category)
                    await session.flush()  # Flush to get the ID
                    field_count += 1
                    print(f"Created field: {field_name}")
                
                # Process subfields
                subfields = field_data.get("subfields", [])
                for subfield_name in subfields:
                    # Check if subfield already exists
                    existing_subfield = await session.execute(
                        select(SubfieldCategory).where(
                            SubfieldCategory.field_id == field_category.id,
                            SubfieldCategory.subfield_name == subfield_name
                        )
                    )
                    
                    if not existing_subfield.scalar_one_or_none():
                        # Create new subfield category
                        subfield_category = SubfieldCategory(
                            id=str(uuid.uuid4()),
                            field_id=field_category.id,
                            subfield_name=subfield_name,
                            description=f"Subfield of {field_name}: {subfield_name}",
                            created_at=datetime.utcnow()
                        )
                        session.add(subfield_category)
                        subfield_count += 1
            
            # Commit all changes
            await session.commit()
            
            print(f"\nDatabase population completed!")
            print(f"Created {field_count} new fields")
            print(f"Created {subfield_count} new subfields")
    
    async def display_summary(self):
        """Display a summary of the populated categories."""
        async with db_manager.get_async_session() as session:
            # Count fields
            field_result = await session.execute(select(FieldCategory))
            fields = field_result.scalars().all()
            
            print(f"\n=== DATABASE SUMMARY ===")
            print(f"Total Fields: {len(fields)}")
            
            for field in fields:
                # Count subfields for this field
                subfield_result = await session.execute(
                    select(SubfieldCategory).where(SubfieldCategory.field_id == field.id)
                )
                subfields = subfield_result.scalars().all()
                
                print(f"  {field.field_name}: {len(subfields)} subfields")


async def main():
    """Main function to populate categories."""
    try:
        # Initialize database manager
        await db_manager.initialize_hybrid_system()
        
        # Create populator and run
        populator = CategoryPopulator()
        await populator.populate_database()
        await populator.display_summary()
        
    except Exception as e:
        print(f"Error during population: {e}")
        raise
    finally:
        await db_manager.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
