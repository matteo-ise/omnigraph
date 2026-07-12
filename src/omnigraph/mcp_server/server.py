from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from omnigraph import __version__
from omnigraph.mcp_server import tools

mcp = FastMCP("omnigraph")
__version__ = __version__


@mcp.tool()
def search(query: str, k: int = 10, mode: str = "hybrid") -> list[dict]:
    """Search files in the knowledge graph.

    Args:
        query: The search query.
        k: The number of results to return.
        mode: The search mode ('hybrid', 'keyword', or 'semantic').
    """
    return tools.search(query, k, mode)


@mcp.tool()
def get_file(path: str) -> dict:
    """Retrieve full text and metadata of an indexed file.

    Args:
        path: Absolute path to the file.
    """
    return tools.get_file(path)


@mcp.tool()
def list_projects() -> list[dict]:
    """List all indexed projects and database stats."""
    return tools.list_projects()


@mcp.tool()
def graph_query(node_id: str, depth: int = 2) -> dict:
    """Query a node's local neighborhood (subgraph).

    Args:
        node_id: The ID of the center node (e.g., 'file:hash' or 'tag:tagname').
        depth: The traversal depth (max distance from center).
    """
    return tools.graph_query(node_id, depth)


@mcp.tool()
def find_related(path: str, k: int = 5) -> list[dict]:
    """Find related files based on shared projects, tags, topics or folder.

    Args:
        path: Absolute path to the file.
        k: Maximum number of related files to return.
    """
    return tools.find_related(path, k)


@mcp.tool()
def reindex(root: str | None = None) -> dict:
    """Manually trigger a full or partial reindexing.

    Args:
        root: Optional absolute path to a specific folder to reindex.
              If omitted, crawls all configured roots.
    """
    return tools.reindex(root)
