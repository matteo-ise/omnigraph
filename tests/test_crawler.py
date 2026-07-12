from pathlib import Path

import pytest

from omnigraph.crawler import walk, IgnoreStack


@pytest.fixture
def temp_tree(tmp_path: Path):
    (tmp_path / "file.txt").write_text("hello")
    (tmp_path / "file.md").write_text("# title")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "nested.txt").write_text("nested")
    (tmp_path / "ignored").mkdir()
    (tmp_path / "ignored" / "secret.txt").write_text("secret")
    (tmp_path / ".gitignore").write_text("ignored/\n")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("git")
    return tmp_path


def test_walk_finds_files(temp_tree: Path):
    entries = walk(temp_tree, extra_ignores=[".git"])
    paths = {e.path.name for e in entries}
    assert "file.txt" in paths
    assert "file.md" in paths
    assert "nested.txt" in paths


def test_walk_respects_gitignore(temp_tree: Path):
    entries = walk(temp_tree, extra_ignores=[".git"])
    paths = {e.path.name for e in entries}
    assert "secret.txt" not in paths


def test_walk_ignores_git_dir(temp_tree: Path):
    entries = walk(temp_tree, extra_ignores=[".git"])
    paths = {e.path.name for e in entries}
    assert "config" not in paths


def test_walk_blocks_system_paths():
    with pytest.raises(ValueError, match="blocked"):
        walk("/etc")


def test_ignore_stack(tmp_path: Path):
    (tmp_path / ".gitignore").write_text("*.log\n")
    (tmp_path / ".omniignore").write_text("private/\n")
    stack = IgnoreStack(tmp_path, extra_patterns=[".git"])
    assert stack.is_ignored(tmp_path / "test.log")
    assert stack.is_ignored(tmp_path / "private" / "data.txt")
    assert stack.is_ignored(tmp_path / ".git" / "config")
    assert not stack.is_ignored(tmp_path / "readme.md")
