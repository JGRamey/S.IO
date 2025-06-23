-- Enhanced Yggdrasil Knowledge System Database Schema
-- Supports broad knowledge domains, complete books, and academic content

-- Create enhanced knowledge categories table
CREATE TABLE knowledge_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR(50) NOT NULL,
    category_name VARCHAR(200) NOT NULL,
    description TEXT,
    parent_category_id UUID REFERENCES knowledge_categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create main texts table with enhanced capabilities
CREATE TABLE yggdrasil_texts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(1000) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    domain VARCHAR(50) NOT NULL,
    language VARCHAR(50) NOT NULL DEFAULT 'english',
    
    -- Content
    content TEXT NOT NULL,
    summary TEXT,
    abstract TEXT,
    
    -- Categorization
    category_id UUID REFERENCES knowledge_categories(id),
    
    -- Enhanced metadata
    author VARCHAR(500),
    authors TEXT[], -- Array for multiple authors
    editor VARCHAR(300),
    translator VARCHAR(300),
    publisher VARCHAR(300),
    publication_year INTEGER,
    publication_date TIMESTAMP WITH TIME ZONE,
    
    -- Identifiers
    isbn VARCHAR(20),
    doi VARCHAR(100),
    arxiv_id VARCHAR(50),
    pmid VARCHAR(20), -- PubMed ID
    
    -- Source information
    source_url VARCHAR(2000),
    source_type VARCHAR(100),
    
    -- Full book support
    is_full_book BOOLEAN DEFAULT FALSE,
    total_pages INTEGER,
    chapter_count INTEGER,
    current_chapter INTEGER,
    chapter_title VARCHAR(500),
    
    -- Text structure
    book_section VARCHAR(100),
    chapter INTEGER,
    verse INTEGER,
    page_number INTEGER,
    
    -- AI and vector capabilities
    embedding_vector FLOAT[],
    qdrant_point_id VARCHAR(100),
    embedding_model VARCHAR(100),
    
    -- Content analysis
    token_count INTEGER,
    word_count INTEGER,
    reading_time_minutes INTEGER,
    difficulty_score FLOAT,
    
    -- Enhanced metadata as arrays/JSON
    keywords TEXT[],
    topics TEXT[],
    themes TEXT[],
    metadata JSONB,
    
    -- Chunking for large texts
    chunk_sequence INTEGER,
    parent_text_id UUID REFERENCES yggdrasil_texts(id),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scraped_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX idx_yggdrasil_domain_type ON yggdrasil_texts(domain, content_type);
CREATE INDEX idx_yggdrasil_category ON yggdrasil_texts(category_id);
CREATE INDEX idx_yggdrasil_author ON yggdrasil_texts(author);
CREATE INDEX idx_yggdrasil_created ON yggdrasil_texts(created_at);
CREATE INDEX idx_yggdrasil_title ON yggdrasil_texts USING GIN(to_tsvector('english', title));
CREATE INDEX idx_yggdrasil_content ON yggdrasil_texts USING GIN(to_tsvector('english', content));
CREATE INDEX idx_yggdrasil_keywords ON yggdrasil_texts USING GIN(keywords);
CREATE INDEX idx_yggdrasil_parent ON yggdrasil_texts(parent_text_id);
CREATE INDEX idx_yggdrasil_book_structure ON yggdrasil_texts(is_full_book, chapter, verse);

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for auto-updating timestamps
CREATE TRIGGER update_yggdrasil_texts_updated_at 
    BEFORE UPDATE ON yggdrasil_texts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create view for easy browsing by domain
CREATE VIEW yggdrasil_by_domain AS
SELECT 
    domain,
    content_type,
    COUNT(*) as text_count,
    COUNT(DISTINCT author) as unique_authors,
    SUM(word_count) as total_words,
    AVG(word_count) as avg_words_per_text
FROM yggdrasil_texts 
WHERE parent_text_id IS NULL  -- Only count main texts, not chunks
GROUP BY domain, content_type
ORDER BY domain, content_type;

-- Create view for full books
CREATE VIEW full_books AS
SELECT 
    id,
    title,
    author,
    domain,
    total_pages,
    chapter_count,
    word_count,
    publication_year,
    created_at
FROM yggdrasil_texts 
WHERE is_full_book = TRUE
ORDER BY created_at DESC;

-- Create view for book chapters
CREATE VIEW book_chapters AS
SELECT 
    t.id,
    t.title as chapter_title,
    t.current_chapter,
    t.content,
    t.word_count,
    p.title as book_title,
    p.author,
    p.id as book_id
FROM yggdrasil_texts t
JOIN yggdrasil_texts p ON t.parent_text_id = p.id
WHERE p.is_full_book = TRUE AND t.current_chapter IS NOT NULL
ORDER BY p.title, t.current_chapter;

-- Insert default knowledge categories
INSERT INTO knowledge_categories (domain, category_name, description) VALUES
('religion', 'Religious Texts', 'Sacred texts and religious literature'),
('philosophy', 'Philosophical Works', 'Philosophical texts and treatises'),
('science', 'Scientific Literature', 'Scientific papers and research'),
('mathematics', 'Mathematical Works', 'Mathematical texts and proofs'),
('history', 'Historical Documents', 'Historical texts and records'),
('literature', 'Literary Works', 'Fiction and literary non-fiction'),
('technology', 'Technical Documentation', 'Technical manuals and documentation'),
('medicine', 'Medical Literature', 'Medical texts and research'),
('law', 'Legal Documents', 'Legal texts and case studies'),
('education', 'Educational Materials', 'Textbooks and educational content');

-- Create function for full-text search
CREATE OR REPLACE FUNCTION search_yggdrasil(search_term TEXT, domain_filter TEXT DEFAULT NULL)
RETURNS TABLE(
    id UUID,
    title VARCHAR(1000),
    author VARCHAR(500),
    domain VARCHAR(50),
    content_type VARCHAR(50),
    excerpt TEXT,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        t.title,
        t.author,
        t.domain,
        t.content_type,
        ts_headline('english', t.content, plainto_tsquery('english', search_term)) as excerpt,
        ts_rank(to_tsvector('english', t.title || ' ' || t.content), plainto_tsquery('english', search_term)) as rank
    FROM yggdrasil_texts t
    WHERE 
        to_tsvector('english', t.title || ' ' || t.content) @@ plainto_tsquery('english', search_term)
        AND (domain_filter IS NULL OR t.domain = domain_filter)
    ORDER BY rank DESC, t.created_at DESC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql;
