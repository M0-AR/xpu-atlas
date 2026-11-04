from xpu_atlas import paper_check
from xpu_atlas.io_utils import FIGURES, RESULTS, ROOT, read_json


def test_generated_results_present_and_consistent():
    analysis = read_json(RESULTS / "analysis.json")
    summary = read_json(RESULTS / "summary.json")
    assert analysis["evidence"]["totals"]["claims"] == 64
    assert summary["headline"]["claims_total"] == "64"
    assert summary["headline"]["verification_rate"] == "73.4%"
    assert summary["headline"]["max_inflation"] == "579x (PPU)"
    assert analysis["bibliometrics"]["terms"]["dpu"]["inflation_factor"] > 100
    assert analysis["bench"]["matmul_peak_gflops"] > 100


def test_figures_exist_and_are_nonempty():
    expected = [
        "fig1_lexical_inflation.png",
        "fig2_publication_trajectories.png",
        "fig3_attention_reallocation.png",
        "fig4_market_economics.png",
        "fig5_evidence_gradient.png",
        "fig6_latency_throughput.png",
    ]
    for name in expected:
        path = FIGURES / name
        assert path.exists(), name
        assert path.stat().st_size > 10_000, name


def test_docs_exist():
    for name in ("EVIDENCE.md", "RESULTS.md"):
        path = ROOT / "docs" / name
        assert path.exists()
        assert path.stat().st_size > 1_000


def test_paper_check_passes():
    assert paper_check.main() == 0
