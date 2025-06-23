#!/bin/bash
# Create convenient shortcuts for frequently accessed files

echo "🔗 Creating convenient shortcuts..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Create shortcuts directory
mkdir -p shortcuts

# Create symbolic links to frequently used files
ln -sf ../mcp/server/yggdrasil_mcp_server.py shortcuts/mcp_server.py
ln -sf ../mcp/client/yggdrasil_mcp_client.py shortcuts/mcp_client.py
ln -sf ../tests/quick_agent_test.py shortcuts/quick_test.py
ln -sf ../tests/test_mcp_agents.py shortcuts/test_agents.py
ln -sf ../config/.env shortcuts/config.env
ln -sf ../sql/yggdrasil_enhanced_schema.sql shortcuts/schema.sql
ln -sf ../docs/guides/MCP_AGENTS_GUIDE.md shortcuts/agents_guide.md
ln -sf ../docs/guides/FINAL_SETUP_GUIDE.md shortcuts/setup_guide.md
ln -sf ../deployment/docker/docker-compose.yml shortcuts/docker-compose.yml

echo "✅ Shortcuts created in shortcuts/ directory:"
ls -la shortcuts/

echo ""
echo "🎯 Quick access examples:"
echo "  python3 shortcuts/quick_test.py"
echo "  python3 shortcuts/mcp_client.py"
echo "  docker-compose -f shortcuts/docker-compose.yml up -d"
echo "  open shortcuts/agents_guide.md"
