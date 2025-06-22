
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
