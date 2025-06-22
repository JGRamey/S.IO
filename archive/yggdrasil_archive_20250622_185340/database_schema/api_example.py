#!/usr/bin/env python3
"""
S.IO Yggdrasil Database API Example
Demonstrates how to use the database schema with your web scraper
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, Tree, Branch, Limb, Resource, ResourceCrossReference
import json
from datetime import datetime

class YggdrasilAPI:
    def __init__(self, database_url="postgresql://user:password@localhost/yggdrasil"):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def add_scraped_resource(self, tree_name, branch_name, limb_name, 
                           title, author=None, content=None, source_url=None, 
                           key_concepts=None, metadata=None):
        """Add a scraped resource to the database"""
        session = self.get_session()
        try:
            # Find the limb
            limb = session.query(Limb)\
                         .join(Branch)\
                         .join(Tree)\
                         .filter(Tree.name == tree_name,
                                Branch.name == branch_name,
                                Limb.name == limb_name)\
                         .first()
            
            if not limb:
                raise ValueError(f"Limb not found: {tree_name}/{branch_name}/{limb_name}")
            
            # Create resource
            resource = Resource(
                limb_id=limb.id,
                title=title,
                author=author,
                content=content,
                source_url=source_url,
                key_concepts=key_concepts or [],
                metadata=metadata or {},
                scraped_at=datetime.utcnow()
            )
            
            session.add(resource)
            session.commit()
            
            print(f"✅ Added resource: {title}")
            return resource.id
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error adding resource: {e}")
            return None
        finally:
            session.close()
    
    def search_resources(self, query, limit=10):
        """Full-text search across resources"""
        session = self.get_session()
        try:
            # Use PostgreSQL full-text search
            results = session.execute(
                text("""
                SELECT r.id, r.title, r.author, r.tree_path, 
                       ts_rank(to_tsvector('english', r.title || ' ' || COALESCE(r.content, '')), 
                               plainto_tsquery('english', :query)) as rank
                FROM resources r
                WHERE to_tsvector('english', r.title || ' ' || COALESCE(r.content, '')) 
                      @@ plainto_tsquery('english', :query)
                ORDER BY rank DESC
                LIMIT :limit
                """), 
                {"query": query, "limit": limit}
            ).fetchall()
            
            return [dict(row) for row in results]
            
        finally:
            session.close()
    
    def get_tree_structure(self, tree_name):
        """Get complete structure for a tree"""
        session = self.get_session()
        try:
            tree = session.query(Tree).filter(Tree.name == tree_name).first()
            if not tree:
                return None
            
            structure = {
                "tree": tree.name,
                "branches": {}
            }
            
            for branch in tree.branches:
                structure["branches"][branch.name] = {
                    "limbs": {}
                }
                
                for limb in branch.limbs:
                    resource_count = len(limb.resources)
                    structure["branches"][branch.name]["limbs"][limb.name] = {
                        "resource_count": resource_count,
                        "resources": [r.title for r in limb.resources[:5]]  # Show first 5
                    }
            
            return structure
            
        finally:
            session.close()
    
    def get_resource_by_path(self, tree_name, branch_name, limb_name, resource_title):
        """Get a specific resource by its path"""
        session = self.get_session()
        try:
            resource = session.query(Resource)\
                             .join(Limb)\
                             .join(Branch)\
                             .join(Tree)\
                             .filter(Tree.name == tree_name,
                                    Branch.name == branch_name,
                                    Limb.name == limb_name,
                                    Resource.title == resource_title)\
                             .first()
            
            if resource:
                return {
                    "id": resource.id,
                    "title": resource.title,
                    "author": resource.author,
                    "content": resource.content,
                    "key_concepts": resource.key_concepts,
                    "tree_path": resource.tree_path,
                    "scraped_at": resource.scraped_at
                }
            return None
            
        finally:
            session.close()

# Example usage for web scraper integration
def example_web_scraper_integration():
    """Example of how to integrate with your web scraper"""
    
    api = YggdrasilAPI("postgresql://localhost/yggdrasil")
    
    # Example: Scraping philosophical texts
    scraped_data = {
        "title": "Meditations",
        "author": "Marcus Aurelius",
        "content": "Sample content of Marcus Aurelius' Meditations...",
        "source_url": "https://example.com/meditations",
        "key_concepts": ["stoicism", "virtue", "self_discipline", "philosophy"]
    }
    
    # Add to database
    resource_id = api.add_scraped_resource(
        tree_name="philosophy",
        branch_name="ancient_philosophy", 
        limb_name="roman_philosophy",
        title=scraped_data["title"],
        author=scraped_data["author"],
        content=scraped_data["content"],
        source_url=scraped_data["source_url"],
        key_concepts=scraped_data["key_concepts"]
    )
    
    print(f"Resource ID: {resource_id}")
    
    # Search for resources
    results = api.search_resources("stoicism")
    print("Search results:", results)
    
    # Get tree structure
    structure = api.get_tree_structure("philosophy")
    print("Philosophy tree structure:", json.dumps(structure, indent=2))

# Example scraper class
class YggdrasilScraper:
    def __init__(self, database_url):
        self.api = YggdrasilAPI(database_url)
    
    def scrape_url(self, url, tree_name, branch_name, limb_name):
        """Scrape a URL and add to database"""
        # Your scraping logic here
        # This is just a placeholder
        
        title = "Scraped Title"
        content = "Scraped content..."
        author = "Scraped Author"
        
        return self.api.add_scraped_resource(
            tree_name=tree_name,
            branch_name=branch_name,
            limb_name=limb_name,
            title=title,
            author=author,
            content=content,
            source_url=url
        )
    
    def bulk_scrape_from_config(self, config_file):
        """Scrape multiple URLs from configuration"""
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        for item in config["urls_to_scrape"]:
            print(f"Scraping: {item['url']}")
            self.scrape_url(
                url=item["url"],
                tree_name=item["tree"],
                branch_name=item["branch"],
                limb_name=item["limb"]
            )

if __name__ == "__main__":
    # Run the example
    example_web_scraper_integration()
