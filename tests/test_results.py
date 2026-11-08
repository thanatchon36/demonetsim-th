"""The committed results/ (seed 7, 600 draws) must carry the headline numbers the paper and README quote."""
import json

import numpy as np
import pandas as pd
import pytest

from analysis import prcc


@pytest.fixture
def summary(root):
    return pd.read_csv(root / "results" / "scenario_summary.csv").set_index("scenario")


def test_shock_bites_77_percent_with_one_sixth_of_indias_disruption(summary):
    s1 = summary.loc["S1"]
    assert s1.hit_med == pytest.approx(0.077, abs=0.0005)
    assert 1 / 7 < s1.liq_index_med / summary.loc["IN16", "liq_index_med"] < 1 / 5
    assert s1.burden_vulnerable_informal_med == pytest.approx(0.90, abs=0.01)


def test_phase_out_with_aml_bites_61_percent_at_no_liquidity_cost(summary):
    s4 = summary.loc["S4"]
    assert s4.hit_med == pytest.approx(0.061, abs=0.0005)
    assert s4.liq_index_med == 0.0


def test_abc_accepts_1214_of_4000_india_draws(root):
    assert len(pd.read_csv(root / "results" / "india_prior_draws.csv")) == 4000
    assert len(pd.read_csv(root / "results" / "india_abc_accepted.csv")) == 1214


def test_disruption_hinges_on_replacement_speed(root):
    res = json.loads((root / "results" / "prcc_s1.json").read_text())
    assert res["liq"]["r_day"] < -0.9
    assert abs(res["hit"]["cap_struct_total"]) > 0.7


def test_prcc_recovers_monotone_relationships():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"a": rng.random(500), "b": rng.random(500), "c": rng.random(500)})
    df["y"] = np.exp(3 * df.a) - 10 * df.b + 0.01 * rng.normal(size=500)
    r = prcc(df, "y", params=["a", "b", "c"])
    assert r["a"] > 0.9 and r["b"] < -0.9 and abs(r["c"]) < 0.2
