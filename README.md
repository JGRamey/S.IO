# Solomon-Sophia: Local AI Spiritual Text Analysis

A comprehensive spiritual text analysis system powered by **local AI models** including Hugging Face Transformers, Ollama, and optional TensorFlow. No external API keys required - everything runs locally for complete privacy and control.

## 🌟 Features

- **Local AI Models**: Uses Hugging Face Transformers and Ollama for completely local processing
- **Multi-Agent System**: Specialized AI agents for different types of spiritual analysis
- **Vector Search**: Semantic search through spiritual texts using local embeddings
- **RESTful API**: FastAPI-based backend with comprehensive endpoints
- **Rich CLI**: Command-line interface for all operations
- **Docker Support**: Complete containerized deployment
- **Privacy-First**: All processing happens locally - no data leaves your machine

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (required for TensorFlow compatibility)
- Docker and Docker Compose (optional but recommended)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Solomon/Backend:Database
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Set up local models:**
   ```bash
   python setup_local_models.py
   ```

4. **Initialize the database:**
   ```bash
   solomon init-db
   ```

5. **Start the services:**
   ```bash
   docker-compose up -d  # Start PostgreSQL, Qdrant, and Ollama
   solomon serve          # Start the API server
   ```

## 🤖 Local AI Models

### Hugging Face Models
- **Language Model**: `facebook/opt-350m` (configurable)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Cache Directory**: `./.cache/huggingface`

### Ollama Local LLM
- **Default Model**: `llama2`
- **Host**: `http://localhost:11434`
- **Automatic fallback**: When Hugging Face models are unavailable

### TensorFlow (Optional)
- **Model**: `google/flan-t5-base`
- **Usage**: Advanced text generation tasks
- **Enable**: Set `USE_TENSORFLOW=True` in `.env`

## 📁 Project Structure

```
solomon/
├── agents/          # AI agent implementations
├── api/            # FastAPI routes and endpoints
├── core/           # Core business logic
├── database/       # Database models and operations
├── services/       # External service integrations
├── cli.py          # Command-line interface
└── main.py         # Application entry point
```

## 🔧 Configuration

The system is configured through environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/solomon

# Hugging Face Models
HF_MODEL_NAME=facebook/opt-350m
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Vector Database
QDRANT_URL=http://localhost:6333

# Optional TensorFlow
USE_TENSORFLOW=False
TF_MODEL_NAME=google/flan-t5-base
```

## 🎯 Usage Examples

### CLI Commands

```bash
# Initialize database
solomon init-db

# Upload spiritual texts
solomon upload-text path/to/spiritual-text.txt

# Query the system
solomon query "What does this text say about meditation?"

# Start API server
solomon serve

# View configuration
solomon config
```

### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Upload text
curl -X POST http://localhost:8000/api/v1/texts/upload \
  -H "Content-Type: application/json" \
  -d '{"content": "Your spiritual text here", "title": "Text Title"}'

# Query texts
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "meditation practices", "limit": 5}'
```

## 🐳 Docker Deployment

The system includes a complete Docker Compose setup:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services included:
- **PostgreSQL**: Main database
- **Qdrant**: Vector database for embeddings
- **Ollama**: Local LLM server
- **Solomon API**: Main application

## 🔍 AI Agents

The system includes specialized agents for different analysis tasks:

- **Base Agent**: Core text analysis functionality
- **Meditation Agent**: Specialized in meditation and mindfulness texts
- **Scripture Agent**: Biblical and religious text analysis
- **Philosophy Agent**: Philosophical text interpretation
- **Wisdom Agent**: General wisdom and spiritual guidance

## 📊 Vector Search

The system uses local embeddings for semantic search:

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Storage**: Qdrant vector database
- **Chunking**: Configurable text chunking for optimal search

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black solomon/

# Lint code
flake8 solomon/

# Type checking
mypy solomon/
```

### Adding New Agents

1. Create agent class in `solomon/agents/`
2. Inherit from `BaseAgent`
3. Implement required methods
4. Register in agent factory

## 🔒 Privacy & Security

- **Local Processing**: All AI inference happens locally
- **No External APIs**: No data sent to third-party services
- **Configurable Models**: Choose your own models and parameters
- **Data Control**: Complete control over your data and processing

## 📚 Documentation

- [Setup Guide](FINAL_SETUP_GUIDE.md) - Comprehensive setup instructions
- [API Documentation](docs/api.md) - Detailed API reference
- [Agent Development](docs/agents.md) - Creating custom agents
- [Deployment Guide](docs/deployment.md) - Production deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Join community discussions
- **Documentation**: Check the docs/ directory for detailed guides

## 🙏 Acknowledgments

- Hugging Face for providing excellent local AI models
- Ollama for local LLM infrastructure
- The open-source AI community for making local AI accessible

---

**Note**: This system is designed for spiritual and educational purposes. All AI responses should be considered as computational analysis rather than authoritative spiritual guidance.
