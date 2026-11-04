from xpu_atlas.claims import chi2_2x2, compute_audit, load_ledger, wilson_interval


def test_ledger_shape_and_uniqueness():
    ledger = load_ledger()
    assert len(ledger["paradigms"]) == 20
    assert len(ledger["sources"]) == 58
    claim_ids = [claim["id"] for paradigm in ledger["paradigms"] for claim in paradigm["claims"]]
    assert len(claim_ids) == 64
    assert len(claim_ids) == len(set(claim_ids))
    source_ids = {source["id"] for source in ledger["sources"]}
    for paradigm in ledger["paradigms"]:
        for claim in paradigm["claims"]:
            assert set(claim["sources"]) <= source_ids


def test_audit_totals_and_rates():
    audit = compute_audit(load_ledger())
    assert audit["totals"] == {"claims": 64, "paradigms": 20, "sources": 58}
    assert sum(audit["status_counts"].values()) == 64
    assert sum(audit["grade_counts"].values()) == 64
    assert audit["status_counts"]["supported"] == 47
    assert abs(audit["verification_rate"] - 47 / 64) < 1e-12
    assert abs(audit["primary_share"] - 13 / 64) < 1e-12


def test_wilson_interval_known_value():
    low, high = wilson_interval(47, 64)
    assert 0.61 < low < 0.62
    assert 0.82 < high < 0.83


def test_chi_square_known_value():
    chi2, p_value = chi2_2x2(2, 31, 11, 20)
    assert abs(chi2 - 6.828) < 0.01
    assert abs(p_value - 0.00897) < 0.001


def test_era_gradient_is_directional():
    audit = compute_audit(load_ledger())
    shares = [audit["by_era"][era]["primary_share"] for era in ("pre-2015", "2015-2020", "2021-2026")]
    assert shares == sorted(shares)
    assert shares[0] < 0.1
    assert shares[-1] > 0.35
