# 🚀 OM-Studio MCP Server

**Enterprise Metadata Governance directly in Claude Desktop.**

OM-Studio is a Model Context Protocol (MCP) server that bridges **OpenMetadata** catalogs with AI Agents. It enables Large Language Models to perform agentic data governance, analyze data lineage, and build live privacy dashboards using real-time metadata.

---

## ✨ Features

- **`discover_data`**: Multi-catalog search for tables and descriptions.
- **`get_ui_context`**: Live schema, PII tags, and quality metrics discovery.
- **`analyze_impact`**: Recursive blast-radius analysis (Lineage Discovery).
- **`check_connection`**: Real-time health check for your OpenMetadata catalog.

---

## 🚀 Quick Start (Production Setup)

The fastest way to run OM-Studio is via `uvx` (No manual installs required).

### 1. Configure Claude Desktop
Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "om-studio": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/CoderRahul01/om-studio-mcp.git",
        "om-studio-mcp",
        "--url", "https://your-openmetadata-url",
        "--token", "your-jwt-token"
      ]
    }
  }
}
```

### 2. Restart Claude
Fully quit Claude (**Cmd+Q**) and relaunch. You will see the **om-studio** tools in your wrench menu.

---

## 🔧 Local Development

If you want to contribute or run locally:

```bash
# Clone and install
git clone https://github.com/CoderRahul01/om-studio-mcp.git
cd om-studio-mcp
uv sync

# Run the server
uv run om-studio --url http://localhost:8585 --token <your_token>
```

---

## 🏛️ Architecture

OM-Studio uses **Lazy Loading** for its internal `openmetadata-ingestion` libraries. This ensures the MCP handshake completes in `< 2 seconds`, bypassing the common 60-second initialization timeout in AI clients.

## 📄 License
MIT © Rahul Pandey
