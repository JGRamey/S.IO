# 🌳 Yggdrasil Knowledge System - Complete Guide

**The Ultimate Knowledge Management & Scraping System**

*Evolved from Solomon's advanced spiritual text analysis to a comprehensive knowledge repository supporting all domains.*

---

## 🎯 **What is Yggdrasil?**

Yggdrasil is an enhanced knowledge management system that combines:
- **Solomon's advanced text analysis capabilities** (vector search, AI features)
- **Broad domain support** (Religion, Philosophy, Science, Literature, etc.)
- **Complete book import** (Gutenberg, PDF, EPUB)
- **Academic content scraping** (arXiv, Wikipedia, Stanford Encyclopedia)
- **Hybrid PostgreSQL + Qdrant storage** for optimal performance

---

## 🏗️ **System Architecture**

### **Database Schema**
```
yggdrasil_texts (main table)
├── Enhanced metadata (ISBN, DOI, arXiv)
├── Vector embeddings (ARRAY(Float))
├── Full book support (chapters, chunking)
├── Multi-author support
└── Rich content analysis

knowledge_categories
├── Hierarchical organization
├── 16 broad domains
└── Extensible structure
```

### **Key Features**
- ✅ **20 Content Types**: From religious texts to research papers
- ✅ **16 Knowledge Domains**: Religion to Technology
- ✅ **Full-Text Search**: With PostgreSQL ranking
- ✅ **Vector Search**: Via Qdrant integration
- ✅ **Complete Books**: Import entire books with chapters
- ✅ **Academic Papers**: arXiv, PubMed, DOI support
- ✅ **Multi-Language**: 19+ language support

---

## 🚀 **Quick Start**

### **1. Start Services**
```bash
cd /Users/grant/Desktop/Solomon/Database/S.IO
./docker-setup.sh start
```

### **2. Verify Database**
```bash
docker exec s-io-postgres psql -U postgres -d yggdrasil -c "SELECT domain, count(*) FROM yggdrasil_texts GROUP BY domain;"
```

### **3. Import Your First Book**
```python
from yggdrasil.scraping.yggdrasil_manager import YggdrasilScrapingManager

manager = YggdrasilScrapingManager()
await manager.initialize()

# Import Alice in Wonderland from Project Gutenberg
result = await manager.import_complete_book(
    source="11",  # Gutenberg ID
    source_type="gutenberg"
)
```

---

## 📚 **Content Import Guide**

### **Project Gutenberg Books**
```python
# Import classic literature
await manager.import_complete_book("1342", "gutenberg")  # Pride & Prejudice
await manager.import_complete_book("2701", "gutenberg")  # Moby Dick
await manager.import_complete_book("1661", "gutenberg")  # Sherlock Holmes
```

### **PDF Books**
```python
# Import local PDF files
await manager.import_complete_book("/path/to/book.pdf", "pdf")
```

### **Academic Papers**
```python
# Scrape arXiv papers and academic content
config = {
    "arxiv_ids": ["2301.07041", "2212.08073"],
    "wikipedia_categories": ["Artificial_intelligence", "Philosophy_of_mind"],
    "stanford_topics": ["consciousness", "machine-learning"]
}

results = await manager.scrape_academic_content(config)
```

### **Wikipedia Articles**
```python
# Import Wikipedia articles as books
await manager.import_complete_book("Artificial_intelligence", "wikipedia")
await manager.import_complete_book("Philosophy", "wikipedia")
```

---

## 🔍 **Search & Query Guide**

### **Full-Text Search**
```sql
-- Search across all content
SELECT * FROM search_yggdrasil('consciousness');

-- Domain-specific search
SELECT * FROM search_yggdrasil('quantum mechanics', 'science');

-- Find philosophy texts
SELECT title, author, word_count 
FROM yggdrasil_texts 
WHERE domain = 'philosophy'
ORDER BY created_at DESC;
```

### **Browse by Domain**
```sql
-- Overview of content by domain
SELECT * FROM yggdrasil_by_domain;

-- Find all complete books
SELECT * FROM full_books ORDER BY created_at DESC;

-- Browse book chapters
SELECT book_title, chapter_title, current_chapter 
FROM book_chapters 
WHERE book_title LIKE '%Alice%'
ORDER BY current_chapter;
```

### **Python Queries**
```python
import psycopg2

conn = psycopg2.connect("postgresql://postgres:JGRsolomon0924$@localhost:5431/yggdrasil")
cursor = conn.cursor()

# Find recent additions
cursor.execute("""
    SELECT title, author, domain, word_count, created_at
    FROM yggdrasil_texts 
    WHERE parent_text_id IS NULL  -- Main texts only
    ORDER BY created_at DESC 
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row[0]} by {row[1]} ({row[2]}) - {row[3]} words")
```

---

## 📊 **Content Organization**

### **Supported Content Types**
- **Religious**: Bible, Quran, Buddhist texts, Hindu texts
- **Academic**: Research papers, journals, theses
- **Literature**: Fiction, poetry, essays
- **Reference**: Wikipedia, encyclopedias, manuals
- **Books**: Fiction/non-fiction, biographies, textbooks

### **Knowledge Domains**
1. **Religion** - Sacred texts and religious literature
2. **Philosophy** - Philosophical works and treatises  
3. **Science** - Scientific papers and research
4. **Mathematics** - Mathematical texts and proofs
5. **History** - Historical documents and records
6. **Literature** - Fiction and literary works
7. **Technology** - Technical documentation
8. **Medicine** - Medical texts and research
9. **Law** - Legal documents and case studies
10. **Education** - Textbooks and educational materials
11. **Psychology** - Psychological research and texts
12. **Politics** - Political science and theory
13. **Economics** - Economic texts and research
14. **Sociology** - Sociological research
15. **Arts** - Art history and criticism
16. **Other** - Miscellaneous content

---

## 🔧 **Advanced Configuration**

### **Chunking Settings**
```python
# Import large book with custom chunking
result = await manager.import_complete_book(
    source="large_book.pdf",
    source_type="pdf",
    chunk_size=8000  # Custom chunk size
)
```

### **Scraping Configuration**
```python
# Comprehensive academic scraping
config = {
    "arxiv_ids": ["2301.07041", "2212.08073"],
    "wikipedia_categories": ["Machine_learning", "Philosophy"],
    "category_limit": 20,  # Articles per category
    "stanford_topics": ["consciousness", "free-will", "determinism"]
}
```

### **Custom Categories**
```sql
-- Add custom knowledge category
INSERT INTO knowledge_categories (domain, category_name, description) 
VALUES ('technology', 'AI Research', 'Artificial Intelligence research papers');
```

---

## 🚀 **Performance & Scaling**

### **Indexes**
- Full-text search on title and content
- Domain and content type indexing
- Author and keyword indexing
- Parent-child relationship indexing

### **Vector Search** (via Qdrant)
```python
# Enable vector embeddings for semantic search
text.embedding_vector = generate_embedding(text.content)
text.qdrant_point_id = store_in_qdrant(text.embedding_vector)
```

### **Database Views**
- `yggdrasil_by_domain` - Content statistics by domain
- `full_books` - Complete book listings
- `book_chapters` - Chapter organization

---

## 💡 **Use Cases**

### **Academic Research**
- Import research papers from arXiv
- Search across academic literature
- Track citations and references
- Organize by research domain

### **Literature Study**
- Import complete books and novels
- Chapter-by-chapter analysis
- Search across literary works
- Track themes and concepts

### **Knowledge Management**
- Organize content by domain
- Full-text search capabilities
- Hierarchical categorization
- Rich metadata support

### **AI Training Data**
- Vector embeddings for ML models
- Structured text data
- Domain-specific datasets
- Content analysis features

---

## 🔧 **Maintenance**

### **Database Backup**
```bash
docker exec s-io-postgres pg_dump -U postgres yggdrasil > yggdrasil_backup.sql
```

### **Update Statistics**
```sql
-- Refresh materialized views if needed
REFRESH MATERIALIZED VIEW IF EXISTS content_stats;

-- Update search indexes
REINDEX INDEX idx_yggdrasil_content;
```

### **Monitor Storage**
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('yggdrasil'));

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 📞 **Connection Details**

- **PostgreSQL**: `localhost:5431`
  - Database: `yggdrasil`
  - User: `postgres`
  - Password: `JGRsolomon0924$`

- **Qdrant**: `localhost:6333`
  - Dashboard: `http://localhost:6333/dashboard`

- **Application**: `localhost:8000`

---

## 🎉 **Success Metrics**

Your Yggdrasil system is working correctly when:
- ✅ All database tables exist and are populated
- ✅ Book imports complete successfully with chunking
- ✅ Academic content scraping retrieves papers/articles
- ✅ Full-text search returns relevant results
- ✅ Vector embeddings are generated and stored
- ✅ Content is properly categorized by domain

---

**🌟 Yggdrasil represents the evolution of your knowledge management system from specialized spiritual text analysis to comprehensive, multi-domain knowledge organization with advanced AI capabilities.**
