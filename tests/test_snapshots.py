from xpu_atlas.io_utils import SNAPSHOTS, read_json, sha256_file


def test_manifest_hashes_match_files():
    manifest = read_json(SNAPSHOTS / "capture_manifest.json")
    assert set(manifest["files"]) == {
        "openalex_counts.json",
        "wikimedia_pageviews.json",
        "yahoo_prices.json",
    }
    for name, record in manifest["files"].items():
        path = SNAPSHOTS / name
        assert path.exists()
        assert sha256_file(path) == record["sha256"]


def test_openalex_shape_and_inflation_semantics():
    payload = read_json(SNAPSHOTS / "openalex_counts.json")
    assert len(payload["terms"]) == 14
    for record in payload["terms"].values():
        assert 1 <= len(record["counts"]) <= 26
        assert 1 <= len(record["counts_unquoted"]) <= 26
        assert all(2000 <= int(year) <= 2025 for year in record["counts"])
        assert record["total_unquoted"] >= record["total"]
        assert record["inflation_factor"] >= 1.0
    assert payload["terms"]["dpu"]["total"] == 1169
    assert payload["terms"]["dpu"]["total_unquoted"] == 219566


def test_wikimedia_shape():
    payload = read_json(SNAPSHOTS / "wikimedia_pageviews.json")
    assert len(payload["articles"]) == 12
    for record in payload["articles"].values():
        assert len(record["views"]) == 70
        assert all(int(value) >= 0 for value in record["views"].values())


def test_yahoo_shape_and_positive_prices():
    payload = read_json(SNAPSHOTS / "yahoo_prices.json")
    assert len(payload["tickers"]) == 8
    for record in payload["tickers"].values():
        assert len(record["prices"]) >= 6
        assert all(float(value) > 0 for value in record["prices"].values())
