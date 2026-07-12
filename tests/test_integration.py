from omnigraph.integration import is_cbm_available, merge_results


def test_cbm_not_available_by_default():
    assert is_cbm_available() is False


def test_merge_results():
    omnigraph = [{"path": "/a.txt", "score": 0.9, "provider": "omnigraph"}]
    cbm = [{"path": "/b.py", "score": 0.8}, {"path": "/a.txt", "score": 0.7}]
    merged = merge_results(omnigraph, cbm)
    assert len(merged) == 2
    paths = {r["path"] for r in merged}
    assert "/a.txt" in paths
    assert "/b.py" in paths
    assert merged[1]["provider"] == "cbm"