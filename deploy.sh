#!/bin/bash
# OM-Studio Production Deployer
# Purpose: Zero-to-Live setup for the OpenMetadata MCP Server

echo "🚀 Initializing OM-Studio Deployment..."

# 1. Check for uv (The high-performance Python package manager)
if ! command -v uv &> /dev/null; then
    echo "📦 'uv' not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Ensure uv is in the path for the rest of the script
    export PATH="$HOME/.local/bin:$PATH"
fi

# 2. Setup Virtual Environment
echo "🧪 Creating virtual environment..."
uv venv
source .venv/bin/activate

# 3. Install Dependencies
echo "📥 Installing production dependencies..."
uv pip install -e .

# 4. Check for .env
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating a template..."
    echo "OM_URL=http://localhost:8585" > .env
    echo "OM_JWT=your_token_here" >> .env
    echo "❌ Please edit the .env file with your real OpenMetadata credentials before restarting Claude."
fi

# 5. Run the Auto-Configurator
echo "🔧 Registering OM-Studio with Claude Desktop..."
uv run setup_claude.py

echo "---------------------------------------------------"
echo "✅ OM-Studio is now registered with Claude Desktop."
echo "🔄 PLEASE RESTART CLAUDE (Cmd+Q) to finalize."
echo "---------------------------------------------------"
