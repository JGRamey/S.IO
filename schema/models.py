"""
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
