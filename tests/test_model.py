"""Accounting identities and comparative statics of the agent-based core."""
import numpy as np
import pandas as pd
import pytest

from demonet_sim_th import (
    SCENARIOS,
    abc_india,
    draw_params,
    honest_side,
    illicit_side,
    monte_carlo,
)

FATES = ["extinguished", "captured", "regularized", "laundered", "displaced"]


@pytest.mark.parametrize("key", list(SCENARIOS))
def test_illicit_fates_and_choices_are_shares_of_the_stock(key):
    rng = np.random.default_rng(0)
    s = SCENARIOS[key]
    acc, choices = illicit_side(rng, s, draw_params(rng, s))
    assert sum(acc[k] for k in FATES) == pytest.approx(1.0)
    assert sum(choices.values()) == pytest.approx(1.0)
    assert acc["hit"] == pytest.approx(acc["extinguished"] + acc["captured"])
    assert all(v >= 0 for v in acc.values())


@pytest.mark.parametrize("key", ["S3", "S4"])
def test_phase_out_causes_no_liquidity_gap_and_no_honest_loss(key):
    rng = np.random.default_rng(1)
    s = SCENARIOS[key]
    h = honest_side(rng, s, draw_params(rng, s))
    assert h["gap_days"] == 0.0 and h["liq_raw"] == 0.0
    assert h["honest_lost"] == 0.0 and h["cross_border_lost"] == 0.0


def mean_hit(cap_struct_total: float, runs: int = 40) -> float:
    rng = np.random.default_rng(2)
    s = SCENARIOS["S1"]
    hits = []
    for _ in range(runs):
        p = draw_params(rng, s)
        p.update(illicit_share=0.10, cap_struct_total=cap_struct_total)
        hits.append(illicit_side(rng, s, p)[0]["hit"])
    return float(np.mean(hits))


def test_bite_falls_as_laundering_capacity_rises():
    """Hypothesis 2: the bite is decreasing in laundering capacity."""
    assert mean_hit(0.0001) > mean_hit(0.05) > mean_hit(0.5)


def test_faster_replacement_shrinks_the_liquidity_gap():
    rng = np.random.default_rng(3)
    s = SCENARIOS["S1"]
    p = draw_params(rng, s)
    slow = honest_side(np.random.default_rng(4), s, {**p, "r_day": 0.004})
    fast = honest_side(np.random.default_rng(4), s, {**p, "r_day": 0.015})
    assert fast["gap_days"] < slow["gap_days"]


def test_monte_carlo_is_reproducible_from_the_seed():
    a = monte_carlo(np.random.default_rng(7), SCENARIOS["S1"], 5)
    b = monte_carlo(np.random.default_rng(7), SCENARIOS["S1"], 5)
    pd.testing.assert_frame_equal(a, b)


def test_abc_keeps_only_draws_near_indias_993_percent_return():
    sims, acc = abc_india(np.random.default_rng(7), draws=60)
    assert len(sims) == 60 and 0 < len(acc) <= 60
    assert ((acc.return_rate - 0.993).abs() <= 0.003).all()
