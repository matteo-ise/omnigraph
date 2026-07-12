from __future__ import annotations

import hashlib
import re
from pathlib import Path

from omnigraph.crawler.walker import FileEntry
from omnigraph.extract.base import ExtractedContent
from omnigraph.graph.models import Edge, FileRecord, Node, Project
from omnigraph.graph.store import GraphStore


class GraphBuilder:
    def __init__(self, store: GraphStore):
        self.store = store

    def build_from_file(self, entry: FileEntry, content: ExtractedContent | None, root: Path):
        file_hash = self._hash_file(entry.path)
        node_id = f"file:{file_hash[:16]}"

        project = self._ensure_project(root)
        folder_node = self._ensure_folder(entry.path.parent, root)

        file_record = FileRecord(
            node_id=node_id,
            path=entry.path,
            mtime=entry.mtime,
            size=entry.size,
            ext=entry.ext,
            sha256=file_hash,
        )
        self.store.upsert_file(file_record)

        self.store.add_edge(Edge(src=project.id, dst=node_id, type="CONTAINS"))
        self.store.add_edge(Edge(src=folder_node.id, dst=node_id, type="CONTAINS"))

        if content:
            self._extract_tags(node_id, content)
            self._extract_topics(node_id, content)

    def _ensure_project(self, root: Path) -> Project:
        project_id = f"project:{hashlib.md5(str(root).encode()).hexdigest()[:12]}"
        project = Project(id=project_id, root=root, name=root.name)
        self.store.upsert_project(project)
        self.store.upsert_node(Node(id=project_id, label=root.name, type="project"))
        return project

    def _ensure_folder(self, folder: Path, root: Path) -> Node:
        try:
            rel = folder.relative_to(root)
            folder_name = str(rel)
        except ValueError:
            folder_name = folder.name

        folder_id = f"folder:{hashlib.md5(str(folder).encode()).hexdigest()[:12]}"
        folder_node = Node(id=folder_id, label=folder_name, type="folder")
        self.store.upsert_node(folder_node)
        return folder_node

    def _extract_tags(self, file_node_id: str, content: ExtractedContent):
        tags = set()
        if "tags" in content.metadata:
            for tag in content.metadata["tags"].split(","):
                tags.add(tag.strip())

        hashtag_pattern = re.compile(r"#(\w+)")
        matches = hashtag_pattern.findall(content.text[:2000])
        tags.update(matches)

        for tag in tags:
            tag_id = f"tag:{tag.lower()}"
            tag_node = Node(id=tag_id, label=tag, type="tag")
            self.store.upsert_node(tag_node)
            self.store.add_edge(Edge(src=file_node_id, dst=tag_id, type="TAGGED"))

    def _extract_topics(self, file_node_id: str, content: ExtractedContent):
        if "title" in content.metadata:
            topic = content.metadata["title"]
            topic_id = f"topic:{hashlib.md5(topic.encode()).hexdigest()[:12]}"
            topic_node = Node(id=topic_id, label=topic, type="topic")
            self.store.upsert_node(topic_node)
            self.store.add_edge(Edge(src=file_node_id, dst=topic_id, type="ABOUT"))

    def _hash_file(self, path: Path) -> str:
        try:
            with open(path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except OSError:
            return hashlib.sha256(str(path).encode()).hexdigest()
