# plan.md - Hybrid Database Schema Implementation Plan

> **Task**: PostgreSQL + Qdrant Hybrid Database System Upgrade 
> **Info**: Claude Sonnet 4 Implementation Guide  
> **Status**: Ready for Development

## 🎯 Task Objectives

**Primary Goal**: Build a scalable hybrid database system combining PostgreSQL's relational strengths with Qdrant's vector search capabilities.

**Success Criteria**:
- [ ] Complete schema deployment on PostgreSQL 16+
- [ ] Functional Qdrant collection with semantic search
- [ ] Working hybrid queries demonstrating integration
- [ ] Performance benchmarks meeting target metrics
- [ ] Documentation for team adoption

## 📋 Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] PostgreSQL 16+ environment setup
- [ ] Qdrant 1.10+ instance deployment
- [ ] Python environment with required dependencies
- [ ] Network connectivity between services validated

### Phase 2: Schema Development (Use Prompts 1-4)
- [ ] Execute Prompt 1: Generate core schema
- [ ] Execute Prompt 2: Populate sample data
- [ ] Execute Prompt 3: Create query examples
- [ ] Execute Prompt 4: Test schema extension
- [ ] Validate all components working together

### Phase 3: Production Readiness
- [ ] Performance tuning applied
- [ ] Security configurations implemented
- [ ] Monitoring and alerting setup
- [ ] Backup and recovery procedures tested
- [ ] Team training completed

## 🔧 Development Instructions for Claude

**When implementing this project**:

1. **Follow the prompts sequentially** - Each builds on the previous
2. **Use exact specifications** - Don't modify table names, constraints, or data types
3. **Include all error handling** - Production-ready code only
4. **Test thoroughly** - Validate each component before proceeding
5. **Document assumptions** - Note any deviations or environment-specific choices

**Code Quality Standards**:
- All SQL must compile in PostgreSQL 16+
- Python code must use async patterns where applicable
- Include comprehensive error handling and logging
- Provide performance optimization comments
- Use consistent naming conventions throughout

- **PostgreSQL**: Handles structured hierarchy, metadata, and relational queries
- **Qdrant**: Manages vector embeddings for semantic text search  
- **Hybrid Efficiency**: Structured navigation via SQL, semantic discovery via vectors
- **Scalability**: Supports multiple subject domains with consistent patterns

### System Requirements
- **PostgreSQL**: Version 16+ (recommended for performance features)
- **Qdrant**: Version 1.10+ (latest API compatibility)
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional vectors)
- **Integration**: Python 3.8+ with `psycopg2` and `qdrant-client`

### Advanced Configuration Options

## Usage Instructions

## 🚀 Quick Start for Claude

Execute these prompts in order to build the complete system:

### Step 1: Generate Core Schema
Copy and paste this exact prompt:

```
You are a database architect creating a production-ready hybrid system. Generate a PostgreSQL + Qdrant schema implementing a 4-level hierarchy (Trees → Branches → Limbs → Leaves) with these exact specifications:

**PostgreSQL Schema:**

1. **Master hierarchy table for Religion:**

## 📊 Project Deliverables

**Expected Outputs from Claude**:
1. **Complete SQL Schema** - All tables, indexes, constraints
2. **Qdrant Configuration** - Collection setup and optimization
3. **Sample Data Scripts** - Realistic test data for validation
4. **Query Examples** - Demonstrating hybrid system capabilities
5. **Migration Scripts** - For schema extensions and updates
6. **Performance Tuning** - Optimization recommendations
7. **Documentation** - Setup, usage, and troubleshooting guides

## 🎯 Performance Targets

**Database Performance**:
- Query response time: <100ms for simple lookups
- Vector search: <500ms for semantic queries
- Hybrid queries: <1000ms for complex joins
- Concurrent users: Support 100+ simultaneous connections
- Data scale: Handle 1M+ content entries efficiently

**System Requirements**:
- PostgreSQL: 4+ CPU cores, 8GB+ RAM, SSD storage
- Qdrant: 8GB+ RAM for 1M vectors, NVMe preferred
- Network: <10ms latency between services
- Uptime: 99.9% availability target

---

## 📝 CLAUDE IMPLEMENTATION PROMPTS

> **Instructions**: Execute these prompts sequentially in Claude Sonnet 4. Each prompt builds on the previous one.

### PROMPT 1: Core Schema Generation

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

### PROMPT 2: Sample Data Population

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

### PROMPT 3: Advanced Query Examples

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

### PROMPT 4: Schema Extension Pattern

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

## 🛠️ IMPLEMENTATION REFERENCE

> **For Claude**: Use this section for technical guidance during implementation

### Architecture Overview

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

## ✅ VALIDATION & TESTING

### Post-Implementation Checklist
- [ ] All SQL executes without errors in PostgreSQL 16+
- [ ] Qdrant collection creates and accepts vectors
- [ ] Sample data loads successfully in both systems
- [ ] Hybrid queries return expected results
- [ ] Performance meets target metrics
- [ ] Error handling works correctly
- [ ] Documentation is complete and accurate

### Testing Scenarios

**Unit Tests**:
- Schema creation and constraint validation
- Data insertion and retrieval accuracy  
- Vector search result consistency
- Performance regression detection

**Integration Tests**:
- Cross-database query coordination
- Transaction boundary behavior
- Concurrent access patterns
- Failover and recovery procedures

**Load Testing**:
- Bulk data insertion performance
- Concurrent query handling
- Memory usage under load
- Search accuracy at scale

---

## 🚨 TROUBLESHOOTING GUIDE

### Common Issues & Solutions

**Vector Dimension Mismatches**:
- Verify embedding model consistency (384 dimensions)
- Check Qdrant collection configuration
- Validate vector generation pipeline

**Slow Hybrid Queries**:
- Analyze PostgreSQL query plans (EXPLAIN ANALYZE)
- Check index usage and optimization
- Review Qdrant search parameters

**Memory Issues in Qdrant**:
- Monitor collection size and growth
- Consider quantization settings
- Review HNSW parameters (m, ef_construct)

**Constraint Violations**:
- Validate data before bulk inserts
- Check hierarchy_table values in CHECK constraint
- Ensure leaf_id references exist

### Emergency Procedures

**System Recovery**:
1. Check service health (PostgreSQL, Qdrant)
2. Validate data integrity with diagnostic queries
3. Review logs for error patterns
4. Execute rollback procedures if needed
5. Contact team lead if issues persist

**Performance Degradation**:
1. Run VACUUM ANALYZE on PostgreSQL
2. Check Qdrant memory usage and optimization
3. Review concurrent connection counts
4. Analyze slow query logs
5. Consider scaling resources if needed

---

## 📖 PROJECT COMPLETION

### Final Deliverables Checklist
- [ ] Complete working hybrid database system
- [ ] All prompts executed successfully
- [ ] Performance benchmarks documented
- [ ] Team training materials prepared
- [ ] Production deployment guide ready
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery tested

### Next Steps After Implementation
1. **Production Deployment**: Follow deployment guide
2. **Team Training**: Schedule knowledge transfer sessions  
3. **Monitoring Setup**: Implement performance tracking
4. **Documentation**: Create user guides and API docs
5. **Scaling Planning**: Prepare for growth and expansion

---

**End of plan.md** - Ready for Claude Sonnet 4 implementation