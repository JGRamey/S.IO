# 🤖 MCP-Integrated AI Agents Guide

**Advanced AI Agents integrated with Model Context Protocol for Intelligent Content Analysis**

*Your complete AI agent system for analyzing, processing, and optimizing content across all knowledge domains.*

---

## 🚀 **What's New with MCP Integration**

The AI agents have been **completely upgraded** to work seamlessly with the MCP server architecture:

- **🔗 MCP Protocol Integration** - All agents accessible through standardized MCP interface
- **⚡ Performance Optimization** - Agents now track performance and optimize automatically
- **🧠 Intelligent Coordination** - Agent orchestrator manages complex multi-agent analyses
- **💾 Storage Intelligence** - Smart storage agent integrated with all analysis workflows
- **📊 Real-time Analytics** - Performance monitoring and optimization recommendations

---

## 🧠 **Available AI Agents**

### **1. Theme Recognition Agent**
- **Purpose**: Identifies universal themes across spiritual and philosophical traditions
- **Specialties**: Cross-cultural analysis, universal patterns, theme coherence
- **Best For**: Comparative religion, philosophical analysis, cultural studies

### **2. Doctrine Analysis Agent** 
- **Purpose**: Analyzes religious doctrines and theological concepts
- **Specialties**: Theological accuracy, denominational differences, historical context
- **Best For**: Religious texts, theological documents, denominational studies

### **3. Fallacy Detection Agent**
- **Purpose**: Identifies logical fallacies and argument weaknesses
- **Specialties**: Logical structure analysis, argument quality assessment
- **Best For**: Philosophical arguments, debates, academic papers

### **4. Translation Tracking Agent**
- **Purpose**: Analyzes translation quality and cultural adaptations
- **Specialties**: Multi-language analysis, cultural sensitivity, translation accuracy
- **Best For**: Translated texts, cross-cultural content, linguistic analysis

### **5. Text Sourcing Agent**
- **Purpose**: Identifies and validates text sources and citations
- **Specialties**: Source verification, authenticity scoring, citation quality
- **Best For**: Academic research, source validation, authenticity verification

### **6. Bias Detection Agent** 🆕
- **Purpose**: Detects various forms of bias in content including cognitive, cultural, and logical biases
- **Specialties**: Confirmation bias, selection bias, cultural supremacy, gender bias, logical fallacies
- **Best For**: Content quality assessment, academic review, fairness evaluation

### **7. Bias Detection**
```python
result = await client.ai_content_analysis(
    text="Content to analyze for bias...",
    analysis_type="bias_detection",
    domain="philosophy",
    metadata={"sensitivity": "high"}
)

# Results include:
# - detected_biases: List of biases found with confidence scores
# - bias_summary: Overall bias assessment and categories
# - recommendations: Suggestions for reducing bias
# - overall_bias_score: Numerical bias score (0.0-1.0)
# - analysis_metadata: Analysis details and statistics
```

### **8. Smart Storage Agent** 🆕
- **Purpose**: AI-powered storage optimization and content analysis
- **Specialties**: Storage strategy decisions, complexity analysis, performance optimization
- **Best For**: Large datasets, performance optimization, intelligent storage

### **9. Agent Orchestrator**
- **Purpose**: Coordinates multiple agents for comprehensive analysis
- **Specialties**: Multi-agent workflows, comprehensive insights, cross-analysis
- **Best For**: Complex documents requiring multiple analysis types

---

## 💻 **Using MCP Agents**

### **1. Through MCP Client (Recommended)**

```python
from yggdrasil_mcp_client import YggdrasilMCPClient

# Initialize client
client = YggdrasilMCPClient()
await client.connect()

# Theme analysis
result = await client.ai_content_analysis(
    text="Your content here...",
    analysis_type="theme_analysis",
    tradition="buddhism",
    domain="religion"
)

# Print formatted results
client.print_analysis_summary(result)

await client.disconnect()
```

### **2. Command Line Interface**

```bash
# Theme analysis
python3 yggdrasil_mcp_client.py ai_analyze \
    --text "Love transcends all boundaries in spiritual traditions" \
    --analysis-type theme_analysis

# Fallacy detection
python3 yggdrasil_mcp_client.py ai_analyze \
    --text "Everyone knows meditation is useless because..." \
    --analysis-type fallacy_detection

# Storage optimization
python3 yggdrasil_mcp_client.py ai_analyze \
    --text "Large philosophical treatise content..." \
    --analysis-type storage_optimization
```

### **3. Batch Analysis**

```python
# Analyze multiple texts
texts = [
    ("Buddhist compassion text", "theme_analysis"),
    ("Christian doctrine excerpt", "doctrine_analysis"), 
    ("Philosophical argument", "fallacy_detection")
]

results = []
for text, analysis_type in texts:
    result = await client.ai_content_analysis(text, analysis_type)
    results.append(result)
```

---

## 🎯 **Analysis Types**

### **Theme Analysis**
```python
result = await client.ai_content_analysis(
    text="Your text...",
    analysis_type="theme_analysis",
    tradition="universal",  # or specific tradition
    domain="spirituality"
)

# Results include:
# - detected_themes: List of identified themes
# - cross_references: Similar themes in other traditions  
# - confidence_scores: AI confidence for each theme
# - universal_patterns: Cross-cultural patterns found
```

### **Doctrine Analysis**
```python
result = await client.ai_content_analysis(
    text="Theological text...",
    analysis_type="doctrine_analysis",
    tradition="christianity",
    metadata={"denomination": "catholic"}
)

# Results include:
# - detected_doctrines: Identified doctrinal concepts
# - tradition_analysis: Tradition-specific insights
# - historical_context: Historical background
# - doctrinal_evolution: How doctrines developed
```

### **Fallacy Detection**
```python
result = await client.ai_content_analysis(
    text="Argumentative text...",
    analysis_type="fallacy_detection",
    domain="philosophy"
)

# Results include:
# - detected_fallacies: List of logical fallacies found
# - logical_structure: Analysis of argument structure
# - argument_quality: Overall argument quality score
# - recommendations: Suggestions for improvement
```

### **Bias Detection**
```python
result = await client.ai_content_analysis(
    text="Content to analyze for bias...",
    analysis_type="bias_detection",
    domain="philosophy",
    metadata={"sensitivity": "high"}
)

# Results include:
# - detected_biases: List of biases found with confidence scores
# - bias_summary: Overall bias assessment and categories
# - recommendations: Suggestions for reducing bias
# - overall_bias_score: Numerical bias score (0.0-1.0)
# - analysis_metadata: Analysis details and statistics
```

### **Storage Optimization**
```python
result = await client.ai_content_analysis(
    text="Large content...",
    analysis_type="storage_optimization",
    url="https://source-url.com"
)

# Results include:
# - storage_strategy: Recommended storage approach
# - confidence_score: AI confidence in decision
# - reasoning: Explanation for decision
# - complexity_metrics: Detailed content analysis
# - optimization_recommendations: Performance suggestions
```

### **Comprehensive Analysis**
```python
result = await client.ai_content_analysis(
    text="Complex philosophical text...",
    analysis_type="comprehensive",
    domain="philosophy",
    tradition="mixed"
)

# Results include:
# - All analysis types combined
# - Cross-references between different analyses
# - Comprehensive insights and patterns
# - Performance statistics
```

---

## 📊 **Performance Monitoring**

### **Get Agent Performance**
```python
# Get performance statistics
performance = await client.get_agent_performance()

print(f"Total analyses: {performance['total_analyses']}")
print(f"Success rate: {performance['overall_success_rate']:.2%}")
print(f"Avg time: {performance['avg_processing_time']:.2f}s")

# Agent-specific performance
for agent, stats in performance['agent_performance'].items():
    print(f"{agent}: {stats['avg_time']:.2f}s avg")
```

### **Available Analysis Types**
```python
# Get list of all available analyses
analysis_types = await client.get_analysis_types()

for analysis in analysis_types:
    print(f"- {analysis['name']}: {analysis['description']}")
```

---

## 🛠️ **Advanced Configuration**

### **Custom Analysis Parameters**

```python
# Advanced theme analysis
result = await client.ai_content_analysis(
    text="Your text...",
    analysis_type="theme_analysis",
    tradition="hinduism",
    domain="religion",
    metadata={
        "enable_cross_reference": True,
        "confidence_threshold": 0.7,
        "max_themes": 10,
        "historical_context": True
    }
)

# Advanced storage optimization
result = await client.ai_content_analysis(
    text="Large dataset...",
    analysis_type="storage_optimization",
    domain="science",
    metadata={
        "estimated_size": 50000000,  # 50MB
        "query_frequency": "high",
        "read_pattern": "random",
        "performance_priority": "speed"
    }
)
```

### **Multi-Agent Workflows**

```python
# Sequential analysis pipeline
text = "Complex philosophical argument about consciousness..."

# Step 1: Analyze themes
themes = await client.ai_content_analysis(text, "theme_analysis")

# Step 2: Detect fallacies  
fallacies = await client.ai_content_analysis(text, "fallacy_detection")

# Step 3: Detect bias
bias = await client.ai_content_analysis(text, "bias_detection")

# Step 4: Optimize storage
storage = await client.ai_content_analysis(text, "storage_optimization")

# Step 5: Comprehensive analysis
comprehensive = await client.ai_content_analysis(text, "comprehensive")
```

---

## 🎨 **Real-World Examples**

### **Example 1: Academic Paper Analysis**

```python
paper_text = """
This paper examines the concept of consciousness across different philosophical
traditions. We argue that materialist approaches fail to account for the
hard problem of consciousness, while dualist theories face interaction problems.
Buddhist philosophy offers a unique perspective through the concept of
vijñāna or consciousness-only doctrine...
"""

# Comprehensive analysis
result = await client.ai_content_analysis(
    text=paper_text,
    analysis_type="comprehensive",
    domain="philosophy",
    tradition="mixed",
    url="https://arxiv.org/abs/example"
)

# Results will include:
# - Philosophical themes identified
# - Any logical fallacies detected
# - Bias detection results
# - Storage optimization recommendations
# - Cross-cultural philosophical insights
```

### **Example 2: Religious Text Processing**

```python
religious_text = """
The Sermon on the Mount presents Jesus' core teachings on love, forgiveness,
and compassion. These teachings parallel similar concepts in other wisdom
traditions, showing universal spiritual principles that transcend specific
religious boundaries...
"""

# Multi-step analysis
theme_result = await client.ai_content_analysis(
    text=religious_text,
    analysis_type="theme_analysis", 
    tradition="christianity",
    domain="religion"
)

doctrine_result = await client.ai_content_analysis(
    text=religious_text,
    analysis_type="doctrine_analysis",
    tradition="christianity",
    metadata={"denomination": "catholic"}
)
```

### **Example 3: Large Book Processing**

```python
book_url = "https://www.gutenberg.org/files/11/11-h/11-h.htm"

# First analyze the source
analysis_result = await client.analyze_url(book_url)

# Then perform intelligent scraping with AI analysis
scrape_result = await client.intelligent_scrape(book_url)

# Finally do storage optimization
storage_result = await client.ai_content_analysis(
    text="Large book content...",
    analysis_type="storage_optimization",
    url=book_url,
    domain="literature"
)
```

---

## 🔧 **Integration with Existing Systems**

### **Custom Agent Development**

```python
# Extend the agent system
from yggdrasil.agents.base import BaseAgent, AgentResult

class CustomAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="custom_analysis",
            description="Custom domain-specific analysis"
        )
    
    async def analyze_text(self, text: str, **kwargs) -> AgentResult:
        # Your custom analysis logic
        results = {"custom_metric": 0.85}
        
        return AgentResult(
            success=True,
            data=results,
            metadata=kwargs
        )

# Register with MCP manager
# (Add to mcp_agent_manager.py)
```

### **API Integration**

```python
# Use as an API service
from fastapi import FastAPI
from yggdrasil_mcp_client import YggdrasilMCPClient

app = FastAPI()

@app.post("/analyze")
async def analyze_content(text: str, analysis_type: str):
    client = YggdrasilMCPClient()
    try:
        result = await client.ai_content_analysis(text, analysis_type)
        return result.analysis
    finally:
        await client.disconnect()
```

---

## 📈 **Performance Optimization**

### **Best Practices**

1. **Reuse Connections**: Keep MCP client connected for multiple analyses
2. **Batch Processing**: Use batch analysis for multiple texts
3. **Appropriate Analysis Types**: Choose specific analyses over comprehensive when possible
4. **Monitor Performance**: Regular check agent performance statistics
5. **Storage Optimization**: Use storage optimization analysis for large datasets

### **Performance Tuning**

```python
# Configure for high performance
client = YggdrasilMCPClient()
await client.connect()

# Batch process for efficiency
texts = ["text1", "text2", "text3"]
results = []

for text in texts:
    result = await client.ai_content_analysis(
        text=text,
        analysis_type="theme_analysis"
    )
    results.append(result)

# Keep connection open for multiple operations
# Only disconnect when done
await client.disconnect()
```

---

## 🎯 **Success Metrics**

Your MCP agent system is working optimally when:

- ✅ **Analysis accuracy > 85%** for domain-specific content
- ✅ **Processing time < 30 seconds** for typical analyses  
- ✅ **Storage decisions > 80% confidence** for optimization
- ✅ **Cross-referencing working** across different traditions
- ✅ **Performance monitoring active** and reporting accurately

---

## 🔗 **Related Files**

- **`yggdrasil/agents/mcp_agent_manager.py`** - Main agent coordination
- **`yggdrasil_mcp_server.py`** - MCP server with agent integration  
- **`yggdrasil_mcp_client.py`** - Client interface for easy usage
- **`test_mcp_agents.py`** - Comprehensive agent testing
- **`yggdrasil/agents/`** - Individual agent implementations

---

**🌟 Your AI agents are now fully integrated with the MCP architecture, providing powerful analysis capabilities with optimal performance and intelligent storage decisions!** 

**Ready to analyze any content type with state-of-the-art AI agents through a standardized, high-performance interface!** 🚀
