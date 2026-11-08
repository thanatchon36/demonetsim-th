"""Denomination size and bulk: the deterministic numbers quoted in Section 2 of the paper."""
import pytest

from demonet_sim_th import bulk_table, denomination_metrics


def pct(note: str) -> float:
    d = denomination_metrics()
    return float(d.loc[d.note == note, "pct_of_gdp_pc"].iloc[0])


def test_thb_1000_is_038_percent_of_gdp_per_capita():
    assert pct("THB 1,000 (TH 2024)") == pytest.approx(0.38, abs=0.005)


def test_thb_1000_is_about_a_quarter_of_the_eur_500_at_withdrawal():
    assert 0.2 < pct("THB 1,000 (TH 2024)") / pct("EUR 500 (EA 2016)") < 0.3


def test_sorted_from_largest_to_smallest():
    d = denomination_metrics()
    assert d.pct_of_gdp_pc.is_monotonic_decreasing


def test_ten_million_baht_in_100s_weighs_90_kg_and_fills_119_litres():
    b = bulk_table().set_index("form")
    assert b.loc["THB 100", "kg"] == pytest.approx(90.0)
    assert b.loc["THB 100", "litres"] == pytest.approx(119, abs=0.5)


def test_withdrawing_the_1000_roughly_doubles_the_bulk():
    b = bulk_table().set_index("form")
    assert 1.8 < b.loc["THB 500", "kg"] / b.loc["THB 1,000", "kg"] < 2.0
    assert b.loc["USDT stablecoin", "kg"] == 0.0
