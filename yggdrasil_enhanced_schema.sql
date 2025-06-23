-- Enhanced Yggdrasil Database Schema with Intelligent Storage Optimization
-- Supports hybrid PostgreSQL + Qdrant storage with dynamic table creation

-- Drop existing schema if recreating
-- DROP SCHEMA IF EXISTS yggdrasil CASCADE;
-- CREATE SCHEMA yggdrasil;

-- Core metadata table for all content (lightweight)
CREATE TABLE IF NOT EXISTS content_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    source_url TEXT NOT NULL UNIQUE,
    author TEXT,
    
    -- Classification
    domain VARCHAR(50) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    
    -- Size and complexity metrics
    estimated_size BIGINT NOT NULL,
    word_count INTEGER,
    character_count INTEGER,
    semantic_complexity FLOAT DEFAULT 0.5,
    topic_coherence FLOAT DEFAULT 0.5,
    information_density FLOAT DEFAULT 0.5,
    query_potential FLOAT DEFAULT 0.5,
    
    -- Storage strategy tracking
    storage_strategy VARCHAR(50) NOT NULL,
    storage_location TEXT, -- table name or Qdrant collection
    qdrant_point_id UUID,
    confidence_score FLOAT DEFAULT 0.5,
    
    -- Performance tracking
    query_count INTEGER DEFAULT 0,
    last_queried TIMESTAMP,
    access_frequency FLOAT DEFAULT 0.0,
    
    -- Content preview for quick access
    content_preview TEXT, -- First 1000 characters
    
    -- Rich metadata
    metadata JSONB DEFAULT '{}',
    tags TEXT[],
    keywords TEXT[],
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    scraped_at TIMESTAMP
);

-- Indexes for content_metadata (optimized for query patterns)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_domain ON content_metadata(domain);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_type ON content_metadata(content_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_size ON content_metadata(estimated_size);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_complexity ON content_metadata(semantic_complexity, query_potential);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_strategy ON content_metadata(storage_strategy);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_performance ON content_metadata(query_count, access_frequency);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_url ON content_metadata(source_url);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_created ON content_metadata(created_at);

-- Full-text search on metadata
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_title_search ON content_metadata USING gin(to_tsvector('english', title));
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_preview_search ON content_metadata USING gin(to_tsvector('english', content_preview));
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_author ON content_metadata USING gin(to_tsvector('english', author));

-- GIN index for JSONB metadata
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_jsonb ON content_metadata USING gin(metadata);

-- Array indexes for tags and keywords
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_tags ON content_metadata USING gin(tags);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata_keywords ON content_metadata USING gin(keywords);

-- Small to medium content storage (full content in PostgreSQL)
CREATE TABLE IF NOT EXISTS postgres_content (
    metadata_id UUID PRIMARY KEY REFERENCES content_metadata(id) ON DELETE CASCADE,
    full_content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL, -- SHA-256 hash for deduplication
    chunked_content JSONB, -- For structured content like books with chapters
    
    -- Processing results
    extracted_entities JSONB,
    topic_analysis JSONB,
    sentiment_scores JSONB,
    
    -- Performance optimizations
    content_tsvector TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', full_content)) STORED,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for postgres_content
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_postgres_content_hash ON postgres_content(content_hash);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_postgres_content_search ON postgres_content USING gin(content_tsvector);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_postgres_content_entities ON postgres_content USING gin(extracted_entities);

-- Qdrant storage mapping (for large content stored as vectors)
CREATE TABLE IF NOT EXISTS qdrant_mappings (
    metadata_id UUID PRIMARY KEY REFERENCES content_metadata(id) ON DELETE CASCADE,
    collection_name VARCHAR(100) NOT NULL,
    point_id UUID NOT NULL,
    vector_dimensions INTEGER NOT NULL,
    chunk_count INTEGER DEFAULT 1,
    
    -- Qdrant-specific metadata
    distance_metric VARCHAR(20) DEFAULT 'cosine',
    embedding_model VARCHAR(100) DEFAULT 'all-MiniLM-L6-v2',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(collection_name, point_id)
);

-- Indexes for qdrant_mappings
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_qdrant_mappings_collection ON qdrant_mappings(collection_name);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_qdrant_mappings_point ON qdrant_mappings(point_id);

-- Dynamic tables registry (tracks dynamically created tables)
CREATE TABLE IF NOT EXISTS dynamic_tables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL UNIQUE,
    domain VARCHAR(50) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    
    -- Table characteristics
    estimated_rows BIGINT DEFAULT 0,
    avg_content_size INTEGER DEFAULT 0,
    total_size_bytes BIGINT DEFAULT 0,
    
    -- Performance metrics
    query_count INTEGER DEFAULT 0,
    avg_query_time_ms FLOAT DEFAULT 0.0,
    last_optimized TIMESTAMP,
    
    -- Schema information
    schema_definition JSONB NOT NULL,
    indexes_definition JSONB DEFAULT '[]',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for dynamic_tables
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dynamic_tables_domain ON dynamic_tables(domain);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dynamic_tables_type ON dynamic_tables(content_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dynamic_tables_performance ON dynamic_tables(query_count, avg_query_time_ms);

-- Query performance tracking
CREATE TABLE IF NOT EXISTS query_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash VARCHAR(64) NOT NULL, -- SHA-256 of normalized query
    query_type VARCHAR(50) NOT NULL, -- 'search', 'filter', 'aggregate', etc.
    
    -- Query characteristics
    target_domain VARCHAR(50),
    storage_strategy VARCHAR(50),
    involves_full_text BOOLEAN DEFAULT FALSE,
    involves_vectors BOOLEAN DEFAULT FALSE,
    
    -- Performance metrics
    execution_time_ms FLOAT NOT NULL,
    rows_returned INTEGER,
    rows_examined INTEGER,
    
    -- Query optimization
    used_indexes TEXT[],
    suggested_optimizations JSONB,
    
    executed_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for query_performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_query_performance_hash ON query_performance(query_hash);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_query_performance_type ON query_performance(query_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_query_performance_time ON query_performance(execution_time_ms);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_query_performance_domain ON query_performance(target_domain);

-- Storage optimization recommendations
CREATE TABLE IF NOT EXISTS optimization_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recommendation_type VARCHAR(50) NOT NULL, -- 'index', 'partition', 'migrate', 'consolidate'
    target_table VARCHAR(100),
    target_domain VARCHAR(50),
    
    -- Recommendation details
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    sql_commands TEXT[],
    expected_benefit TEXT,
    risk_level VARCHAR(20) DEFAULT 'low', -- 'low', 'medium', 'high'
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'applied', 'rejected', 'failed'
    applied_at TIMESTAMP,
    applied_by VARCHAR(100),
    
    -- Performance prediction
    estimated_improvement_percent FLOAT,
    confidence_score FLOAT DEFAULT 0.5,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for optimization_recommendations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_optimization_rec_type ON optimization_recommendations(recommendation_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_optimization_rec_status ON optimization_recommendations(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_optimization_rec_table ON optimization_recommendations(target_table);

-- Enhanced Views for Analytics and Monitoring

-- Content overview by storage strategy
CREATE OR REPLACE VIEW storage_strategy_overview AS
SELECT 
    storage_strategy,
    domain,
    COUNT(*) as content_count,
    AVG(estimated_size) as avg_size,
    SUM(estimated_size) as total_size,
    AVG(query_count) as avg_query_count,
    AVG(semantic_complexity) as avg_complexity,
    AVG(confidence_score) as avg_confidence
FROM content_metadata
GROUP BY storage_strategy, domain
ORDER BY storage_strategy, domain;

-- Performance analytics view
CREATE OR REPLACE VIEW performance_analytics AS
SELECT 
    cm.domain,
    cm.storage_strategy,
    COUNT(cm.id) as content_items,
    AVG(cm.query_count) as avg_queries_per_item,
    AVG(qp.execution_time_ms) as avg_query_time_ms,
    COUNT(DISTINCT qp.query_hash) as unique_query_patterns
FROM content_metadata cm
LEFT JOIN query_performance qp ON qp.target_domain = cm.domain
GROUP BY cm.domain, cm.storage_strategy
ORDER BY avg_query_time_ms DESC;

-- Storage utilization view
CREATE OR REPLACE VIEW storage_utilization AS
SELECT 
    'postgres' as storage_type,
    COUNT(pc.metadata_id) as item_count,
    pg_size_pretty(SUM(length(pc.full_content::text))) as storage_used,
    AVG(length(pc.full_content)) as avg_item_size
FROM postgres_content pc
UNION ALL
SELECT 
    'qdrant' as storage_type,
    COUNT(qm.metadata_id) as item_count,
    'N/A (Vector DB)' as storage_used,
    AVG(cm.estimated_size) as avg_item_size
FROM qdrant_mappings qm
JOIN content_metadata cm ON cm.id = qm.metadata_id;

-- Functions for Intelligent Operations

-- Function to suggest storage strategy for new content
CREATE OR REPLACE FUNCTION suggest_storage_strategy(
    p_size BIGINT,
    p_complexity FLOAT DEFAULT 0.5,
    p_domain VARCHAR(50) DEFAULT 'general',
    p_query_potential FLOAT DEFAULT 0.5
) RETURNS VARCHAR(50) AS $$
DECLARE
    strategy VARCHAR(50);
BEGIN
    -- Logic for storage strategy suggestion
    IF p_size < 50000 THEN
        strategy := 'postgres_full';
    ELSIF p_size > 50000000 THEN
        strategy := 'qdrant_vectors';
    ELSIF p_complexity > 0.7 AND p_query_potential > 0.8 THEN
        strategy := 'hybrid_optimal';
    ELSIF p_domain IN ('science', 'philosophy', 'literature') AND p_size > 1000000 THEN
        strategy := 'hybrid_optimal';
    ELSE
        strategy := 'postgres_metadata';
    END IF;
    
    RETURN strategy;
END;
$$ LANGUAGE plpgsql;

-- Function for intelligent search across storage types
CREATE OR REPLACE FUNCTION intelligent_search(
    p_query TEXT,
    p_domain VARCHAR(50) DEFAULT NULL,
    p_limit INTEGER DEFAULT 20
) RETURNS TABLE (
    id UUID,
    title TEXT,
    author TEXT,
    domain VARCHAR(50),
    storage_strategy VARCHAR(50),
    relevance_score FLOAT,
    content_preview TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH search_results AS (
        -- Search in metadata
        SELECT 
            cm.id,
            cm.title,
            cm.author,
            cm.domain,
            cm.storage_strategy,
            ts_rank(to_tsvector('english', cm.title || ' ' || COALESCE(cm.content_preview, '')), 
                   plainto_tsquery('english', p_query)) as relevance_score,
            cm.content_preview
        FROM content_metadata cm
        WHERE 
            (p_domain IS NULL OR cm.domain = p_domain)
            AND to_tsvector('english', cm.title || ' ' || COALESCE(cm.content_preview, '')) 
                @@ plainto_tsquery('english', p_query)
        
        UNION ALL
        
        -- Search in PostgreSQL full content
        SELECT 
            cm.id,
            cm.title,
            cm.author,
            cm.domain,
            cm.storage_strategy,
            ts_rank(pc.content_tsvector, plainto_tsquery('english', p_query)) as relevance_score,
            cm.content_preview
        FROM content_metadata cm
        JOIN postgres_content pc ON pc.metadata_id = cm.id
        WHERE 
            (p_domain IS NULL OR cm.domain = p_domain)
            AND pc.content_tsvector @@ plainto_tsquery('english', p_query)
    )
    SELECT DISTINCT
        sr.id,
        sr.title,
        sr.author,
        sr.domain,
        sr.storage_strategy,
        MAX(sr.relevance_score) as relevance_score,
        sr.content_preview
    FROM search_results sr
    GROUP BY sr.id, sr.title, sr.author, sr.domain, sr.storage_strategy, sr.content_preview
    ORDER BY relevance_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to track query performance
CREATE OR REPLACE FUNCTION track_query_performance(
    p_query_hash VARCHAR(64),
    p_query_type VARCHAR(50),
    p_target_domain VARCHAR(50),
    p_execution_time_ms FLOAT,
    p_rows_returned INTEGER DEFAULT 0,
    p_storage_strategy VARCHAR(50) DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO query_performance (
        query_hash, query_type, target_domain, storage_strategy,
        execution_time_ms, rows_returned, executed_at
    ) VALUES (
        p_query_hash, p_query_type, p_target_domain, p_storage_strategy,
        p_execution_time_ms, p_rows_returned, NOW()
    );
    
    -- Update access frequency for content
    UPDATE content_metadata 
    SET 
        query_count = query_count + 1,
        last_queried = NOW(),
        access_frequency = query_count::FLOAT / EXTRACT(EPOCH FROM (NOW() - created_at)) * 86400 -- queries per day
    WHERE (p_target_domain IS NULL OR domain = p_target_domain);
END;
$$ LANGUAGE plpgsql;

-- Function to generate optimization recommendations
CREATE OR REPLACE FUNCTION generate_optimization_recommendations() RETURNS INTEGER AS $$
DECLARE
    rec_count INTEGER := 0;
BEGIN
    -- Clear old recommendations
    DELETE FROM optimization_recommendations WHERE status = 'pending' AND created_at < NOW() - INTERVAL '7 days';
    
    -- Recommend indexes for frequently queried domains
    INSERT INTO optimization_recommendations (
        recommendation_type, target_domain, title, description, 
        estimated_improvement_percent, confidence_score
    )
    SELECT 
        'index',
        domain,
        'Add composite index for ' || domain || ' queries',
        'Frequently queried domain would benefit from optimized indexing',
        25.0,
        0.8
    FROM (
        SELECT domain, AVG(execution_time_ms) as avg_time, COUNT(*) as query_count
        FROM query_performance 
        WHERE executed_at > NOW() - INTERVAL '24 hours'
        GROUP BY domain
        HAVING COUNT(*) > 50 AND AVG(execution_time_ms) > 100
    ) slow_domains
    WHERE NOT EXISTS (
        SELECT 1 FROM optimization_recommendations 
        WHERE target_domain = slow_domains.domain 
        AND recommendation_type = 'index' 
        AND status = 'pending'
    );
    
    GET DIAGNOSTICS rec_count = ROW_COUNT;
    
    -- Recommend migration for oversized PostgreSQL content
    INSERT INTO optimization_recommendations (
        recommendation_type, target_table, title, description,
        estimated_improvement_percent, confidence_score
    )
    SELECT 
        'migrate',
        'postgres_content',
        'Migrate large content to Qdrant',
        'Large content items in PostgreSQL would perform better in vector storage',
        40.0,
        0.9
    FROM content_metadata cm
    JOIN postgres_content pc ON pc.metadata_id = cm.id
    WHERE cm.estimated_size > 10000000 -- > 10MB
    AND NOT EXISTS (
        SELECT 1 FROM optimization_recommendations 
        WHERE recommendation_type = 'migrate' 
        AND status = 'pending'
    )
    LIMIT 1;
    
    GET DIAGNOSTICS rec_count = rec_count + ROW_COUNT;
    
    RETURN rec_count;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic optimization

-- Trigger to update access patterns
CREATE OR REPLACE FUNCTION update_access_patterns() RETURNS TRIGGER AS $$
BEGIN
    -- Update metadata when content is accessed
    UPDATE content_metadata 
    SET 
        query_count = query_count + 1,
        last_queried = NOW()
    WHERE id = COALESCE(NEW.metadata_id, OLD.metadata_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to postgres_content
DROP TRIGGER IF EXISTS trig_update_access_patterns ON postgres_content;
CREATE TRIGGER trig_update_access_patterns
    AFTER SELECT ON postgres_content
    FOR EACH ROW EXECUTE FUNCTION update_access_patterns();

-- Auto-generate recommendations periodically
CREATE OR REPLACE FUNCTION auto_generate_recommendations() RETURNS VOID AS $$
BEGIN
    PERFORM generate_optimization_recommendations();
END;
$$ LANGUAGE plpgsql;

-- Performance monitoring setup
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Initial sample data for testing
INSERT INTO content_metadata (
    title, source_url, domain, content_type, estimated_size, 
    storage_strategy, content_preview, confidence_score
) VALUES 
(
    'Sample Philosophy Text',
    'https://example.com/philosophy',
    'philosophy',
    'academic_paper',
    500000,
    'hybrid_optimal',
    'This is a sample philosophical text discussing consciousness and reality...',
    0.85
),
(
    'Sample Literature Book', 
    'https://example.com/book',
    'literature',
    'book',
    15000000,
    'qdrant_vectors',
    'Chapter 1: It was the best of times, it was the worst of times...',
    0.92
),
(
    'Sample Technical Document',
    'https://example.com/tech-doc',
    'technology',
    'documentation',
    75000,
    'postgres_full',
    'This technical documentation covers advanced programming concepts...',
    0.78
) 
ON CONFLICT (source_url) DO NOTHING;

-- Final optimizations
ANALYZE content_metadata;
ANALYZE postgres_content;
ANALYZE qdrant_mappings;
ANALYZE dynamic_tables;

-- Summary of schema
DO $$
BEGIN
    RAISE NOTICE 'Enhanced Yggdrasil schema created successfully!';
    RAISE NOTICE 'Tables: content_metadata, postgres_content, qdrant_mappings, dynamic_tables';
    RAISE NOTICE 'Views: storage_strategy_overview, performance_analytics, storage_utilization';
    RAISE NOTICE 'Functions: suggest_storage_strategy, intelligent_search, track_query_performance';
    RAISE NOTICE 'Ready for intelligent storage management!';
END $$;
