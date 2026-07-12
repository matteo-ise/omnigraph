from __future__ import annotations

import typer
from rich import print
from rich.table import Table

from omnigraph import __version__

app = typer.Typer(
    name="omnigraph",
    help="Local knowledge graph across all your drives.",
    no_args_is_help=True,
)


def _version_callback(value: bool):
    if value:
        print(f"omnigraph {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
):
    pass


@app.command()
def crawl(
    root: str = typer.Option(None, "--root", help="Root directory to crawl."),
    watch: bool = typer.Option(False, "--watch", help="Watch for changes after crawling."),
    dry_run: bool = typer.Option(False, "--dry-run", help="List files without indexing."),
):
    """Crawl directories and build the knowledge graph."""
    from omnigraph.config import get_config
    from omnigraph.crawler.walker import walk
    from omnigraph.extract import extract_file
    from omnigraph.graph.builder import GraphBuilder
    from omnigraph.graph.store import GraphStore
    from omnigraph.search.keyword import KeywordSearch

    config = get_config()
    roots = [root] if root else config.roots

    if dry_run:
        for r in roots:
            from pathlib import Path

            entries = walk(Path(r))
            count = 0
            for e in entries:
                print(f"[cyan]{e.path}[/] ({e.size} bytes)")
                count += 1
            print(f"\n[bold]{count}[/] files found.")
        return

    config.ensure_db_dir()
    with GraphStore(config.db_path) as store:
        builder = GraphBuilder(store)
        kw = KeywordSearch(store.conn)
        from omnigraph.embed.engine import Embedder
        from omnigraph.search.semantic import SemanticSearch
        embedder = Embedder()
        semantic = SemanticSearch(store.conn, dimension=embedder.dimension)

        total = 0
        from rich.progress import Progress
        with Progress() as progress:
            task = progress.add_task("[cyan]Crawling...", total=None)
            for r in roots:
                from pathlib import Path

                root_path = Path(r)
                entries = walk(root_path)
                for entry in entries:
                    content = extract_file(entry.path)
                    node_id = builder.build_from_file(entry, content, root_path)
                    if content:
                        title = content.metadata.get("title", entry.path.name)
                        file_id = node_id
                        kw.index(file_id, str(entry.path), title, content.text)
                        
                        semantic.delete(file_id)
                        chunks = content.chunks if content.chunks else embedder.chunk_text(content.text)
                        if chunks:
                            embeddings = embedder.encode(chunks)
                            for i, emb in enumerate(embeddings):
                                semantic.index(f"{file_id}:chunk{i}", emb)
                            
                            # Add SIMILAR_TO edges
                            for emb in embeddings:
                                results = semantic.search(emb, k=3)
                                for r in results:
                                    other_id = r.file_id.split(":")[0] + ":" + r.file_id.split(":")[1] # e.g. file:hash
                                    if other_id != file_id and r.score > 0.8:
                                        from omnigraph.graph.models import Edge
                                        store.add_edge(Edge(src=file_id, dst=other_id, type="SIMILAR_TO", properties={"score": r.score}))
                                        store.add_edge(Edge(src=other_id, dst=file_id, type="SIMILAR_TO", properties={"score": r.score}))
                    
                    total += 1
                    progress.update(task, advance=1)
                    if total % 1000 == 0:
                        store.commit()
        store.commit()
        print(f"[bold green]Indexed {total} files.[/]")

        if watch:
            print("[yellow]Watching for changes... (Ctrl+C to stop)[/]")
            from omnigraph.watch.watcher import FileWatcher

            watcher = FileWatcher(store, roots[0])
            watcher.run()


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query."),
    limit: int = typer.Option(10, "--limit", help="Number of results."),
    mode: str = typer.Option("keyword", "--mode", help="Search mode: hybrid|keyword|semantic."),
):
    """Search the knowledge graph."""
    from omnigraph.config import get_config
    from omnigraph.graph.store import GraphStore
    from omnigraph.search.hybrid import hybrid_search

    config = get_config()
    with GraphStore(config.db_path) as store:
        results = hybrid_search(store.conn, query, k=limit, mode=mode)

        table = Table(title=f"Search: '{query}' ({mode})")
        table.add_column("Path", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Snippet", style="dim")

        for r in results:
            table.add_row(r.path, f"{r.score:.4f}", r.snippet[:80])

        print(table)


@app.command()
def show(
    path: str = typer.Argument(..., help="File path."),
):
    """Show details of an indexed file."""
    from omnigraph.config import get_config
    from omnigraph.graph.store import GraphStore

    config = get_config()
    with GraphStore(config.db_path) as store:
        file_rec = store.get_file(path)
        if file_rec is None:
            print("[red]File not found in index.[/]")
            return

        from pathlib import Path

        from omnigraph.extract import extract_file

        content = extract_file(Path(path))
        print(f"[bold]Path:[/] {file_rec.path}")
        print(f"[bold]Size:[/] {file_rec.size} bytes")
        print(f"[bold]Ext:[/] {file_rec.ext}")
        print(f"[bold]Node ID:[/] {file_rec.node_id}")
        if content:
            print(f"[bold]Type:[/] {content.metadata.get('type', 'unknown')}")
            print("\n[bold]Text (first 500 chars):[/]")
            print(content.text[:500])


@app.command()
def graph(
    node_id: str = typer.Argument(..., help="Node ID to start from."),
    depth: int = typer.Option(2, "--depth", help="Traversal depth."),
):
    """Show the local neighborhood of a node."""
    from omnigraph.config import get_config
    from omnigraph.graph.store import GraphStore

    config = get_config()
    with GraphStore(config.db_path) as store:
        node = store.get_node(node_id)
        if node is None:
            print("[red]Node not found.[/]")
            return

        neighbors = store.query_neighbors(node_id, depth=depth)
        print(f"[bold]Center:[/] {node.label} ({node.type})")

        if not neighbors:
            print("[dim]No neighbors found.[/]")
            return

        table = Table(title=f"Neighborhood (depth={depth})")
        table.add_column("ID", style="dim")
        table.add_column("Label", style="cyan")
        table.add_column("Type", style="green")

        for n in neighbors:
            table.add_row(n.id, n.label, n.type)

        print(table)


@app.command()
def stats():
    """Show database statistics."""
    from omnigraph.config import get_config
    from omnigraph.graph.store import GraphStore

    config = get_config()
    with GraphStore(config.db_path) as store:
        s = store.get_stats()
        print(f"[bold]Nodes:[/] {s['nodes']}")
        print(f"[bold]Edges:[/] {s['edges']}")
        print(f"[bold]Files:[/] {s['files']}")
        print(f"[bold]Projects:[/] {s['projects']}")


@app.command()
def reindex(
    root: str = typer.Option(None, "--root", help="Specific root to reindex."),
):
    """Manually trigger a full or partial reindex."""
    from pathlib import Path

    from omnigraph.config import get_config
    from omnigraph.crawler.walker import walk
    from omnigraph.extract import extract_file
    from omnigraph.graph.builder import GraphBuilder
    from omnigraph.graph.store import GraphStore
    from omnigraph.search.keyword import KeywordSearch

    config = get_config()
    roots = [Path(root)] if root else config.roots
    total = 0

    with GraphStore(config.db_path) as store:
        builder = GraphBuilder(store)
        kw = KeywordSearch(store.conn)
        from omnigraph.embed.engine import Embedder
        from omnigraph.search.semantic import SemanticSearch
        embedder = Embedder()
        semantic = SemanticSearch(store.conn, dimension=embedder.dimension)

        for r in roots:
            entries = walk(r)
            for entry in entries:
                content = extract_file(entry.path)
                node_id = builder.build_from_file(entry, content, r)
                if content:
                    title = content.metadata.get("title", entry.path.name)
                    file_id = node_id
                    kw.index(file_id, str(entry.path), title, content.text)

                    semantic.delete(file_id)
                    chunks = content.chunks if content.chunks else embedder.chunk_text(content.text)
                    if chunks:
                        embeddings = embedder.encode(chunks)
                        for i, emb in enumerate(embeddings):
                            semantic.index(f"{file_id}:chunk{i}", emb)

                        for emb in embeddings:
                            results = semantic.search(emb, k=3)
                            for res in results:
                                other_id = res.file_id.split(":")[0] + ":" + res.file_id.split(":")[1]
                                if other_id != file_id and res.score > 0.8:
                                    from omnigraph.graph.models import Edge
                                    store.add_edge(Edge(src=file_id, dst=other_id, type="SIMILAR_TO", properties={"score": res.score}))
                                    store.add_edge(Edge(src=other_id, dst=file_id, type="SIMILAR_TO", properties={"score": res.score}))

                total += 1
                if total % 1000 == 0:
                    store.commit()

        store.commit()
        print(f"[bold green]Reindexed {total} files.[/]")


@app.command()
def serve(
    port: int = typer.Option(8765, "--port", help="Port number."),
    web: bool = typer.Option(False, "--web", help="Start web UI instead of MCP server."),
):
    """Start the MCP server or web UI."""
    if web:
        import uvicorn

        from omnigraph.web.app import create_app

        fastapi_app = create_app()
        print(f"[bold green]Web UI at http://localhost:{port}[/]")
        uvicorn.run(fastapi_app, host="0.0.0.0", port=port)
    else:
        from omnigraph.mcp_server.server import mcp

        mcp.run()


if __name__ == "__main__":
    app()
