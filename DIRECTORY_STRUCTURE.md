# 📁 S.IO Directory Structure

**Clean, organized directory structure for the Yggdrasil Knowledge Management System**

---

## 🗂️ **Root Directory Overview**

```
S.IO/
├── 📄 README.md                     # Main project documentation
├── 📄 DIRECTORY_STRUCTURE.md        # This file
├── 📁 yggdrasil/                    # Core application code
├── 📁 mcp/                          # MCP server and client
├── 📁 config/                       # Configuration files
├── 📁 sql/                          # Database schemas
├── 📁 tests/                        # Test suite
├── 📁 docs/                         # Documentation
├── 📁 scripts/                      # Utility scripts
├── 📁 deployment/                   # Docker and deployment
├── 📁 examples/                     # Usage examples
├── 📁 archive/                      # Legacy/backup files
└── 📁 READMEfiles/                  # Legacy documentation
```

---

## 🧠 **Core Application (`yggdrasil/`)**

```
yggdrasil/
├── 📄 __init__.py                   # Package initialization
├── 📄 config.py                     # Application configuration
├── 📄 cli.py                        # Command-line interface
├── 📁 agents/                       # AI agents
│   ├── 📄 base.py                   # Base agent class
│   ├── 📄 theme_recognition.py      # Theme analysis agent
│   ├── 📄 doctrine_analysis.py      # Doctrine analysis agent
│   ├── 📄 fallacy_detection.py      # Fallacy detection agent
│   ├── 📄 translation_tracking.py   # Translation analysis agent
│   ├── 📄 text_sourcing.py          # Text sourcing agent
│   ├── 📄 smart_storage_agent.py    # Storage optimization agent
│   ├── 📄 orchestrator.py           # Agent orchestrator
│   └── 📄 mcp_agent_manager.py      # MCP agent manager
├── 📁 database/                     # Database models and operations
├── 📁 scraping/                     # Web scraping modules
└── 📁 api/                          # API endpoints
```

---

## 🔗 **MCP Integration (`mcp/`)**

```
mcp/
├── 📁 server/
│   └── 📄 yggdrasil_mcp_server.py   # MCP server implementation
└── 📁 client/
    └── 📄 yggdrasil_mcp_client.py   # MCP client implementation
```

**Purpose**: Model Context Protocol integration for AI agent orchestration

---

## ⚙️ **Configuration (`config/`)**

```
config/
├── 📄 .env                          # Environment variables
├── 📄 pyproject.toml                # Python project configuration
├── 📄 requirements.txt              # Python dependencies
├── 📄 alembic.ini                   # Alembic migration configuration
└── 📁 alembic/                      # Database migration files
```

**Purpose**: All configuration files and environment setup

---

## 🗃️ **Database (`sql/`)**

```
sql/
├── 📄 yggdrasil_schema.sql          # Basic database schema
└── 📄 yggdrasil_enhanced_schema.sql # Enhanced schema with AI features
```

**Purpose**: Database schemas and SQL files

---

## 🧪 **Testing (`tests/`)**

```
tests/
├── 📄 test_intelligent_yggdrasil.py # Comprehensive system tests
├── 📄 test_mcp_agents.py            # MCP agent integration tests
├── 📄 test_yggdrasil_system.py      # System functionality tests
└── 📄 quick_agent_test.py           # Quick connectivity tests
```

**Purpose**: Complete test suite for all system components

---

## 📚 **Documentation (`docs/`)**

```
docs/
├── 📁 guides/
│   ├── 📄 AGENTS_INTEGRATION_SUMMARY.md  # Agent integration guide
│   ├── 📄 FINAL_SETUP_GUIDE.md           # Complete setup guide
│   ├── 📄 INTELLIGENT_YGGDRASIL_GUIDE.md # Intelligent features guide
│   ├── 📄 MCP_AGENTS_GUIDE.md            # MCP agents usage guide
│   ├── 📄 YGGDRASIL_GUIDE.md             # Core system guide
│   ├── 📄 WEBSCRAPING_GUIDE.md           # Web scraping guide
│   └── 📄 PYTHON312_UPGRADE_GUIDE.md     # Python upgrade guide
├── 📁 api/                               # API documentation (future)
└── 📁 development/                       # Development documentation (future)
```

**Purpose**: Comprehensive documentation and user guides

---

## 🔧 **Scripts (`scripts/`)**

```
scripts/
└── 📄 scraping_bridge.py            # Scraping bridge utility
```

**Purpose**: Utility scripts and tools for system maintenance

---

## 🚀 **Deployment (`deployment/`)**

```
deployment/
└── 📁 docker/
    ├── 📄 docker-compose.yml        # Docker Compose configuration
    ├── 📄 Dockerfile               # Docker image definition
    ├── 📄 postgres.Dockerfile      # PostgreSQL Docker image
    └── 📄 init.sql                 # Database initialization
```

**Purpose**: Docker containers and deployment configuration

---

## 📖 **Examples (`examples/`)**

```
examples/
└── 📁 usage/                        # Usage examples (future expansion)
```

**Purpose**: Example implementations and tutorials

---

## 📦 **Archive (`archive/`)**

```
archive/
└── 📁 [307 files]                   # Legacy Solomon project files
```

**Purpose**: Safely archived legacy files from Solomon project

---

## 🗂️ **Legacy (`READMEfiles/`)**

```
READMEfiles/
├── 📄 README_ENHANCED.md            # Enhanced README
├── 📄 README_ENHANCED_FINAL.md      # Final enhanced README
└── 📄 README_YGGDRASIL.md           # Yggdrasil-specific README
```

**Purpose**: Legacy documentation files

---

## 📍 **Key File Locations**

### **Essential Files**
- **Main README**: `/README.md`
- **MCP Server**: `/mcp/server/yggdrasil_mcp_server.py`
- **MCP Client**: `/mcp/client/yggdrasil_mcp_client.py`
- **Configuration**: `/config/.env`
- **Database Schema**: `/sql/yggdrasil_enhanced_schema.sql`

### **AI Agents**
- **All agents**: `/yggdrasil/agents/`
- **Agent manager**: `/yggdrasil/agents/mcp_agent_manager.py`
- **Smart storage**: `/yggdrasil/agents/smart_storage_agent.py`

### **Testing**
- **Quick test**: `/tests/quick_agent_test.py`
- **Full test suite**: `/tests/test_*.py`

### **Documentation**
- **Usage guides**: `/docs/guides/`
- **MCP guide**: `/docs/guides/MCP_AGENTS_GUIDE.md`
- **Setup guide**: `/docs/guides/FINAL_SETUP_GUIDE.md`

---

## 🎯 **Navigation Tips**

### **Starting Development**
1. **Read**: `/README.md` for project overview
2. **Setup**: Follow `/docs/guides/FINAL_SETUP_GUIDE.md`
3. **Configure**: Update `/config/.env` with your settings
4. **Test**: Run `/tests/quick_agent_test.py`

### **Working with Agents**
1. **Guide**: Read `/docs/guides/MCP_AGENTS_GUIDE.md`
2. **Test**: Run `/tests/test_mcp_agents.py`
3. **Use**: Import from `/mcp/client/yggdrasil_mcp_client.py`

### **Database Operations**
1. **Schema**: Apply `/sql/yggdrasil_enhanced_schema.sql`
2. **Migrations**: Use `/config/alembic/`
3. **Docker**: Start with `/deployment/docker/docker-compose.yml`

### **Adding Features**
1. **Agents**: Add to `/yggdrasil/agents/`
2. **Tests**: Add to `/tests/`
3. **Documentation**: Add to `/docs/guides/`
4. **Examples**: Add to `/examples/`

---

## 🛡️ **Organization Benefits**

### **Clear Separation**
- **✅ Core code** isolated in `yggdrasil/`
- **✅ MCP components** in dedicated `mcp/` folder
- **✅ Configuration** centralized in `config/`
- **✅ Documentation** organized in `docs/`

### **Easy Navigation**
- **✅ Logical grouping** by functionality
- **✅ Consistent naming** conventions
- **✅ Clear file purposes** and locations
- **✅ Scalable structure** for future growth

### **Development Workflow**
- **✅ Quick testing** with `/tests/quick_agent_test.py`
- **✅ Comprehensive testing** with full test suite
- **✅ Easy deployment** with Docker configuration
- **✅ Clear documentation** path for all features

---

## 🚀 **Next Steps**

1. **✅ Directory structure** is now clean and organized
2. **✅ Files are logically grouped** by functionality
3. **✅ Documentation is accessible** and comprehensive
4. **✅ Testing is straightforward** with clear entry points
5. **✅ Development workflow** is streamlined

**Your S.IO project now has a professional, maintainable directory structure!** 🌟
