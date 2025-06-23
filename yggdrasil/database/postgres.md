-- Database: Yggdrasil

-- DROP DATABASE IF EXISTS "Yggdrasil";

CREATE DATABASE "Yggdrasil"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    ICU_LOCALE = 'und'
    LOCALE_PROVIDER = 'icu'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;


Example layout/categorization for "Spiritual_Texts" table 
--Could use the same exact layout and categories for additional tables inside the Yggdrasil PostgreSQL database
source_id
title
author
publication_year
language
field
subfield
source_type
edition
publisher
isbn
doi
page_count
created_at
updated_at
content_id
content_text
embedding
chunk_sequence
token_count
agent_id
model_name
model_version
status
query_id
query_text
response_text
retrieved_source_ids
query_timestamp
response_time_ms
Here's the example code for the table:
-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Table to store source metadata
CREATE TABLE sources (
    source_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    publication_year INTEGER CHECK (publication_year > 0),
    language VARCHAR(50) NOT NULL,
    field VARCHAR(100) NOT NULL,
    subfield VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- e.g., book, article, manuscript, papyrus
    edition VARCHAR(50),
    publisher VARCHAR(255),
    isbn VARCHAR(13),
    doi VARCHAR(100),
    page_count INTEGER CHECK (page_count >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store content and embeddings for RAG
CREATE TABLE content (
    content_id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(source_id) ON DELETE CASCADE,
    content_text TEXT NOT NULL,
    embedding VECTOR(1536), -- For OpenAI embeddings (e.g., text-embedding-ada-002)
    chunk_sequence INTEGER NOT NULL, -- Order of chunks for large texts
    token_count INTEGER NOT NULL CHECK (token_count >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store AI agent configurations
CREATE TABLE agents (
    agent_id SERIAL PRIMARY KEY,
    language VARCHAR(50) NOT NULL,
    subfield VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    status VARCHAR(50) NOT NULL, -- e.g., trained, fine-tuned, active
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store query logs for performance tracking
CREATE TABLE query_logs (
    query_id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(agent_id),
    query_text TEXT NOT NULL,
    response_text TEXT,
    retrieved_source_ids INTEGER[] REFERENCES sources(source_id),
    query_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER CHECK (response_time_ms >= 0)
);

-- Indexes for efficient querying
CREATE INDEX idx_sources_field_subfield ON sources (field, subfield);
CREATE INDEX idx_sources_language ON sources (language);
CREATE INDEX idx_content_source_id ON content (source_id);
CREATE INDEX idx_content_embedding ON content USING hnsw (embedding vector_cosine_ops); -- HNSW index for vector similarity
CREATE INDEX idx_agents_language_subfield ON agents (language, subfield);
CREATE INDEX idx_query_logs_agent_id ON query_logs (agent_id);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update the updated_at timestamp
CREATE TRIGGER update_sources_timestamp
    BEFORE UPDATE ON sources
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_agents_timestamp
    BEFORE UPDATE ON agents
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Comments for documentation
COMMENT ON TABLE sources IS 'Stores metadata for all sources, including books, articles, manuscripts, images, audio transcripts, video transcripts, etc.';
COMMENT ON TABLE content IS 'Stores text chunks and their embeddings for Retrieval Augmented Generation (RAG).';
COMMENT ON TABLE agents IS 'Stores configurations for AI agents tailored to languages and subfields.';
COMMENT ON TABLE query_logs IS 'Logs queries and responses for performance tracking and analysis.';