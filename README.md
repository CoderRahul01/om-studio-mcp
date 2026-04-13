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

## 🛠️ Troubleshooting & FAQ

### 1. "An executable named om-studio-mcp is not provided"
This happens if you try to run the package name instead of the command.
- **Fix**: Ensure your `args` in the config uses `om-studio` (the command) after the `--from` git URL (the package).

### 2. "Failed to resolve --with requirement"
This usually means the GitHub URL is incorrect or the repository is private/non-existent.
- **Fix**: Double-check that your URL points to `https://github.com/CoderRahul01/om-studio-mcp.git`.

### 3. Connection timeouts (60s errors)
OM-Studio uses **Lazy Loading** to prevent this. If you still see it:
- **Fix**: Check your `mcp_debug.log`. Ensure your OpenMetadata instance is reachable and not behind a slow VPN.

### 4. Authentication Errors (401/403)
- **Fix**: Verify your `OM_JWT` has "Ingestion Bot" or "Admin" permissions in OpenMetadata.

---

## 🏛️ Architecture

OM-Studio is optimized for **speed and stability**:
- **Lazy Loading**: Heavy metadata libraries are only loaded when a tool is called, ensuring the initial handshake happens in `< 2 seconds`.
- **Extreme Safeguarding**: Recursively handles `requests.Response` objects to prevent runtime crashes.

## 📄 License
MIT © Rahul Pandey
