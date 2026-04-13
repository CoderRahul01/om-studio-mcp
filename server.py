import os
import json
import sys
import argparse
import requests
from pathlib import Path

# --- BOOTSTRAP: Version 2.1 Diagnostics ---
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

# Global Config Storage
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
    # 1. Handle raw requests.Response objects
    if hasattr(obj, 'json') and callable(obj.json):
        try:
            return obj.json()
        except:
            return {"error": "Failed to parse Response JSON", "text": getattr(obj, 'text', '')[:200]}
    
    # 2. Handle Pydantic V2 models
    if hasattr(obj, 'model_dump') and callable(obj.model_dump):
        return obj.model_dump()
    
    # 3. Handle Pydantic V1 models
    if hasattr(obj, 'dict') and callable(obj.dict):
        return obj.dict()
    
    # 4. Handle standard list/dict
    if isinstance(obj, (dict, list)):
        return obj
        
    # 5. Fallback for primitive types or unknowns
    return str(obj)

@mcp.tool()
def check_connection() -> str:
    """Health check tool to verify the connection to the OpenMetadata server."""
    try:
        # BYPASS SDK: Direct REST call avoids internal SDK subscripting bugs
        headers = {
            "Authorization": f"Bearer {CONFIG['token']}",
            "Content-Type": "application/json"
        }
        url = f"{CONFIG['url'].rstrip('/')}/api/v1/system/version"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = safeguard_data(resp)
            return json.dumps({
                "status": "healthy", 
                "version": data,
                "mcp_version": "2.1-HARDENED"
            }, indent=2)
        else:
            return json.dumps({
                "status": "degraded", 
                "code": resp.status_code,
                "message": resp.text[:200]
            }, indent=2)
            
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)

@mcp.tool()
def analyze_impact(table_fqn: str) -> str:
    """Performs a blast-radius analysis (lineage) for a table."""
    from metadata.generated.schema.entity.data.table import Table
    om = get_om_client()
    try:
        lineage = om.get_lineage_by_name(entity=Table, fqn=table_fqn)
        data = safeguard_data(lineage)
        
        # Safe extraction
        if isinstance(data, dict):
            return json.dumps(data.get('edges', []), indent=2)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Lineage Error: {e}"

@mcp.tool()
def discover_data(query: str) -> str:
    """Search for tables by name or description."""
    from metadata.generated.schema.entity.data.table import Table
    om = get_om_client()
    try:
        results = om.list_entities(entity=Table, limit=10)
        data = safeguard_data(results)
        
        entities = []
        if isinstance(data, dict):
            entities = data.get('entities', [])
        elif isinstance(data, list):
            entities = data
            
        return json.dumps([{"name": r.get('name') if isinstance(r, dict) else getattr(r, 'name', 'unknown'), 
                            "fqn": r.get('fullyQualifiedName') if isinstance(r, dict) else getattr(r, 'fullyQualifiedName', 'unknown')} 
                           for r in entities], indent=2)
    except Exception as e:
        return f"Discovery Error: {e}"

@mcp.tool()
def get_ui_context(table_fqn: str) -> str:
    """Fetches full schema, tags, and metadata for a table."""
    from metadata.generated.schema.entity.data.table import Table
    om = get_om_client()
    try:
        table = om.get_by_name(entity=Table, fqn=table_fqn, fields=["columns", "tags"])
        if not table: return "Table not found."
        
        data = safeguard_data(table)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Context Error: {e}"

def main():
    parser = argparse.ArgumentParser(description="OM-Studio MCP Server")
    parser.add_argument("--url", default=CONFIG["url"], help="OpenMetadata URL")
    parser.add_argument("--token", default=CONFIG["token"], help="OpenMetadata JWT Token")
    args = parser.parse_args()

    CONFIG["url"] = args.url
    CONFIG["token"] = args.token

    debug_log(f"🚀 VERIFIED VERSION: 2.1 - HARDENED")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()