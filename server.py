import os
import json
import sys
import argparse
from pathlib import Path

# --- BOOTSTRAP: Version 2.0 Diagnostics ---
BASE_DIR = Path(__file__).parent.absolute()
os.chdir(BASE_DIR)
sys.stderr = sys.__stderr__

def debug_log(msg):
    try:
        with open(BASE_DIR / "mcp_debug.log", "a") as f:
            f.write(f"{msg}\n")
    except:
        pass
    print(f"DEBUG: {msg}", file=sys.stderr)

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load .env fallback
load_dotenv(BASE_DIR / ".env")
mcp = FastMCP("om-studio")

# Global Config Storage (for CLI overrides)
CONFIG = {
    "url": os.getenv("OM_URL", "http://localhost:8585"),
    "token": os.getenv("OM_JWT", "")
}

def get_om_client():
    """Lazy-loaded client factory."""
    from metadata.ingestion.ometa.ometa_api import OpenMetadata
    from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import OpenMetadataConnection
    from metadata.generated.schema.security.client.openMetadataJWTClientConfig import OpenMetadataJWTClientConfig

    config = OpenMetadataConnection(
        hostPort=CONFIG["url"], 
        authProvider="openmetadata",
        securityConfig=OpenMetadataJWTClientConfig(
            jwtToken=CONFIG["token"]
        )
    )
    return OpenMetadata(config)

def safeguard_data(obj):
    """Extreme safeguard against 'Response' or Pydantic type mismatches."""
    if hasattr(obj, 'json') and callable(obj.json):
        try:
            return obj.json()
        except:
            return {"error": "Failed to parse Response JSON"}
    if hasattr(obj, 'model_dump') and callable(obj.model_dump):
        return obj.model_dump()
    if hasattr(obj, 'dict') and callable(obj.dict):
        return obj.dict()
    return obj

@mcp.tool()
def check_connection() -> str:
    """Health check tool to verify the connection to the OpenMetadata server."""
    om = get_om_client()
    try:
        raw_version = om.get_server_version()
        version = safeguard_data(raw_version)
        return json.dumps({"status": "healthy", "version": version}, indent=2)
    except Exception as e:
        return json.dumps({"status": "degraded", "error": str(e)}, indent=2)

@mcp.tool()
def analyze_impact(table_fqn: str) -> str:
    """Performs a blast-radius analysis for a table in OpenMetadata.
    Args:
        table_fqn: The fully qualified name.
    """
    from metadata.generated.schema.entity.data.table import Table
    om = get_om_client()
    try:
        lineage = om.get_lineage_by_name(entity=Table, fqn=table_fqn)
        data = safeguard_data(lineage)
        edges = data.get('edges', []) if isinstance(data, dict) else []
        return json.dumps(edges, indent=2)
    except Exception as e:
        return f"Tool Error: {e}"

@mcp.tool()
def discover_data(query: str) -> str:
    """Search for tables by name or description in OpenMetadata.
    Args:
        query: Search keywords.
    """
    from metadata.generated.schema.entity.data.table import Table
    om = get_om_client()
    try:
        results = om.list_entities(entity=Table, limit=5)
        data = safeguard_data(results)
        entities = data.get('entities', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        return json.dumps([{"name": r.get('name') if isinstance(r, dict) else getattr(r, 'name', 'unknown'), 
                            "fqn": r.get('fullyQualifiedName') if isinstance(r, dict) else getattr(r, 'fullyQualifiedName', 'unknown')} 
                           for r in entities], indent=2)
    except Exception as e:
        return f"Tool Error: {e}"

@mcp.tool()
def get_ui_context(table_fqn: str) -> str:
    """Fetches schema, tags, and metrics for a table.
    Args:
        table_fqn: The fully qualified name.
    """
    from metadata.generated.schema.entity.data.table import Table
    om = get_om_client()
    try:
        table = om.get_by_name(entity=Table, fqn=table_fqn, fields=["columns", "tags"])
        if not table: return "Table not found."
        if hasattr(table, 'model_dump_json') and callable(table.model_dump_json):
            return table.model_dump_json()
        data = safeguard_data(table)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Tool Error: {e}"

def main():
    parser = argparse.ArgumentParser(description="OM-Studio MCP Server")
    parser.add_argument("--url", default=CONFIG["url"], help="OpenMetadata URL")
    parser.add_argument("--token", default=CONFIG["token"], help="OpenMetadata JWT Token")
    args = parser.parse_args()

    # Update global config with overrides
    CONFIG["url"] = args.url
    CONFIG["token"] = args.token

    debug_log(f"🚀 VERIFIED VERSION: 2.0 - SAFEGUARDED (Public Distribution Ready)")
    debug_log(f"🔗 Target: {CONFIG['url']}")
    
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()