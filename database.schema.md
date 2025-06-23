# Hybrid Database Schema Guide: PostgreSQL + Qdrant

## Overview

This guide provides structured prompts for creating a scalable hybrid database system that combines PostgreSQL's relational capabilities with Qdrant's vector search performance. The system implements a hierarchical knowledge structure (Trees → Branches → Limbs → Leaves) optimized for semantic content discovery.

### Architecture Benefits

- **PostgreSQL**: Handles structured hierarchy, metadata, and relational queries
- **Qdrant**: Manages vector embeddings for semantic text search
- **Hybrid Efficiency**: Structured navigation via SQL, semantic discovery via vectors
- **Scalability**: Supports multiple subject domains with consistent patterns

### System Requirements

- **PostgreSQL**: Version 16+ (recommended for performance features) ## Make sure dockerfiles use 16+ 
- **Qdrant**: Version 1.10+ (latest API compatibility)
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional vectors)
- **Integration**: Python 3.12 with `psycopg2` and `qdrant-client`

## Usage Instructions

### Quick Start
1. Execute prompts sequentially in Claude
2. Deploy SQL to PostgreSQL 16+
3. Configure Qdrant collection via provided code
4. Test hybrid queries to verify integration
5. Scale by adding new subject hierarchies

### Validation Checklist
- [ ] SQL compiles without errors in PostgreSQL
- [ ] Qdrant collection creates successfully
- [ ] Hybrid queries return expected results
- [ ] Indexes perform as expected under load

---

## Prompt 1: Core Schema Generation

```
You are a database architect creating a production-ready hybrid system. Generate a PostgreSQL + Qdrant schema implementing a 4-level hierarchy (Trees → Branches → Limbs → Leaves) with these exact specifications:

**PostgreSQL Schema:**

1. **Master hierarchy table for Religion:**
```sql
CREATE TABLE religion_hierarchy (
    id SERIAL PRIMARY KEY,
    branch VARCHAR(100) NOT NULL,
    limb VARCHAR(100) NOT NULL,
    leaf VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_religion_path UNIQUE (branch, limb, leaf)
);

CREATE INDEX idx_religion_branch ON religion_hierarchy (branch);
CREATE INDEX idx_religion_limb ON religion_hierarchy (branch, limb);
```

2. **Template hierarchy tables (subject1 through subject8):**
   - Identical structure to religion_hierarchy
   - Replace 'religion' with 'subject1', 'subject2', etc.
   - Include same constraints and indexes

3. **Content metadata table:**
```sql
CREATE TABLE content_metadata (
    id SERIAL PRIMARY KEY,
    hierarchy_table VARCHAR(50) NOT NULL,
    leaf_id INTEGER NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content_summary VARCHAR(500) NOT NULL,
    chunk_number INTEGER DEFAULT 1,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_content_chunk UNIQUE (hierarchy_table, leaf_id, content_type, chunk_number),
    CONSTRAINT valid_hierarchy_table CHECK (
        hierarchy_table IN (
            'religion_hierarchy', 'subject1_hierarchy', 'subject2_hierarchy',
            'subject3_hierarchy', 'subject4_hierarchy', 'subject5_hierarchy',
            'subject6_hierarchy', 'subject7_hierarchy', 'subject8_hierarchy'
        )
    )
);

CREATE INDEX idx_content_hierarchy ON content_metadata (hierarchy_table, leaf_id);
CREATE INDEX idx_content_type ON content_metadata (content_type);
CREATE INDEX idx_content_created ON content_metadata (created_at DESC);
```

**Qdrant Configuration:**

Create collection `content_vectors` with:
- Vector size: 384 (all-MiniLM-L6-v2 compatible)
- Distance: Cosine
- HNSW parameters: m=16, ef_construct=200
- Payload schema:
  - content_id (integer): Links to content_metadata.id
  - hierarchy_table (string): Source table name
  - leaf_id (integer): Hierarchy leaf reference
  - content_type (string): Content classification
  - chunk_number (integer): Content chunk identifier
  - word_count (integer): Text length metadata

Provide complete SQL for all tables and Python code for Qdrant collection setup.
```

---

## Prompt 2: Sample Data Population

```
Using the hybrid schema from Prompt 1, generate realistic sample data for the Religion domain:

**PostgreSQL Sample Data:**

1. **religion_hierarchy (6 diverse entries):**
   - Christianity/Protestant-Baptist/Doctrines
   - Christianity/Protestant-Baptist/Practices
   - Christianity/Catholic/Theology
   - Islam/Sunni/Beliefs
   - Judaism/Orthodox/Traditions
   - Buddhism/Theravada/Teachings

2. **content_metadata (8 content entries):**
   - 3 entries for Baptist Doctrines (multi-chunk content)
   - 2 entries for Catholic Theology
   - 2 entries for Islamic Beliefs
   - 1 entry for Buddhist Teachings
   - Include realistic titles, summaries (100-300 words), and word counts

**Qdrant Sample Data:**

Generate Python code using qdrant-client v1.10 to:
1. Create 8 vector points corresponding to content_metadata entries
2. Use placeholder vectors: `[round(i*0.01, 3) for i in range(384)]` pattern
3. Include all payload fields with correct data types
4. Demonstrate batch upsert for efficiency

Include SQL INSERT statements and complete Python upsert code with error handling.
```

---

## Prompt 3: Advanced Query Examples

```
Create three production-ready query patterns demonstrating the hybrid system's capabilities:

**Query 1: PostgreSQL Hierarchy Navigation**
- Find all content under "Christianity/Protestant-Baptist" branch
- Include content counts by type
- Order by creation date (newest first)
- Use efficient JOIN with proper indexing

**Query 2: Semantic Search + Metadata Filtering**
- Qdrant: Search for content similar to "baptism salvation doctrine"
- PostgreSQL: Filter results by content_type='Doctrine' and recent creation (last 90 days)
- Combine results with hierarchy context (branch/limb/leaf names)
- Return top 10 matches with similarity scores

**Query 3: Cross-Subject Content Discovery**
- Qdrant: Find semantically similar content across ALL hierarchies
- PostgreSQL: Group results by hierarchy_table and content_type
- Include content diversity metrics (unique branches/limbs represented)
- Demonstrate pagination for large result sets

Provide:
- Optimized SQL with EXPLAIN ANALYZE suggestions
- Python code using async qdrant-client for performance
- Error handling and connection management
- Performance benchmarking comments
```

---

## Prompt 4: Schema Extension Pattern

```
Demonstrate how to extend the hybrid system for a new subject domain called "Science":

**Requirements:**
1. Create science_hierarchy table with same structure as religion_hierarchy
2. Update content_metadata CHECK constraint to include 'science_hierarchy'
3. Add sample Science data (Physics/Quantum-Mechanics/Theories, etc.)
4. Provide migration script for zero-downtime deployment
5. Include rollback procedures

**Deliverables:**
- DDL for new table creation
- ALTER statements for constraint updates
- Sample data INSERT statements
- Migration validation queries
- Performance impact assessment

Focus on production deployment considerations:
- Transaction boundaries for atomic changes
- Index creation strategies (CONCURRENTLY where applicable)
- Constraint validation timing
- Backup recommendations before migration
```

---

## Advanced Configuration Options

### Performance Tuning

**PostgreSQL Optimizations:**
- Partitioning strategies for content_metadata (by hierarchy_table or date)
- Connection pooling configuration (PgBouncer recommended)
- Query plan analysis and index optimization
- VACUUM and ANALYZE scheduling

**Qdrant Optimizations:**
- Collection sharding for >1M vectors
- Quantization settings for memory efficiency
- Batch size tuning for bulk operations
- Backup and replication strategies

### Production Deployment

**Infrastructure Requirements:**
- PostgreSQL: 4+ CPU cores, 8GB+ RAM, SSD storage
- Qdrant: 8GB+ RAM for 1M vectors, NVMe storage preferred
- Network: Low-latency connection between services
- Monitoring: Query performance, vector search latency, storage growth

**Security Considerations:**
- Database user roles and permissions
- API key management for Qdrant
- SSL/TLS encryption for data in transit
- Backup encryption and retention policies

### Troubleshooting Guide

**Common Issues:**
1. **Vector dimension mismatches**: Verify embedding model consistency
2. **Slow hybrid queries**: Check index usage and query plans
3. **Memory issues in Qdrant**: Review collection size and quantization
4. **Constraint violations**: Validate data before bulk inserts

**Monitoring Queries:**
- Content distribution by hierarchy
- Vector search performance metrics
- Storage utilization trends
- Query execution time analysis

### Extension Patterns

**Adding New Subjects:**
1. Follow subject hierarchy naming convention
2. Update CHECK constraints atomically
3. Bulk load initial data efficiently
4. Validate cross-subject query performance

**Content Type Extensions:**
- Document types: PDF, DOCX, HTML processing
- Media types: Image, audio metadata handling
- Structured data: JSON, XML content integration
- Real-time updates: Change data capture patterns

---

## Testing Framework

### Unit Tests
- Schema creation and constraint validation
- Data insertion and retrieval accuracy
- Vector search result consistency
- Performance regression detection

### Integration Tests
- Cross-database query coordination
- Transaction boundary behavior
- Concurrent access patterns
- Failover and recovery procedures

### Load Testing
- Bulk data insertion performance
- Concurrent query handling
- Memory usage under load
- Search accuracy at scale

## Additional Updates ## - Ask for permission before implementing or starting

Create agents to help with data organization and management

Create agents to help with data analysis and processing

Create agents to help with data visualization and presentation

Create agents to help with data storage and retrieval

Create agents to help with data security and privacy

Create agents to help with data backup and recovery

Create agents to help with data compression and optimization

Create agents to help with data migration and transfer

Create agents to help with data indexing and search

Update MCP with new agents and functions

Update APIs (Qdrant and Postgresql) with new endpoints and functions

## Later implement:

RAG System