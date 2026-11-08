#!/usr/bin/env python3
"""
DemonetSim-TH  v1.0  (November 2026)
====================================
A stylized policy-simulation toolkit for a *hypothetical* demonetization of
Thailand's 1,000-baht banknote, loosely calibrated to India's 2016 episode.

READ FIRST
----------
* Every default number in this file is an ILLUSTRATIVE ASSUMPTION or a rough,
  memory-based approximation (no live data were used). Replace them with
  verified data - e.g. Bank of Thailand statistics on banknotes in circulation
  by denomination - before using any output.
* The model is a thinking tool for research design and hypothesis generation.
  It is NOT a forecast of what would happen in Thailand.

Modules
-------
1. denomination_metrics()  value of large notes relative to GDP per capita
2. bulk_table()            weight / volume of moving 10 million baht
3. logistics_mc()          extra notes, printing cost, seigniorage (Thailand)
4. honest_side()           liquidity disruption + unconverted honest wealth
5. illicit_side()          agent-based choices of illicit cash holders
6. monte_carlo()           scenario engine with parameter uncertainty
7. abc_india()             approximate Bayesian computation vs India's 99.3 %
8. main()                  runs everything, writes CSV + PNG files

Usage
-----
    pip install numpy pandas matplotlib
    python demonet_sim_th.py --draws 600 --seed 7 --out out
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 1. Denomination metrics (approximate figures - verify before citing)
# ---------------------------------------------------------------------------
DENOMS = pd.DataFrame(
    [
        # note, value (LCU), GDP per capita (LCU, approx), LCU per USD (period avg), status
        ("THB 1,000 (TH 2024)", 1_000, 265_000, 35.3, "current - under discussion"),
        ("THB 500 (TH 2024)", 500, 265_000, 35.3, "current"),
        ("INR 1,000 (IN 2016)", 1_000, 117_000, 67.2, "demonetized - shock"),
        ("INR 2,000 (IN 2023)", 2_000, 190_000, 82.6, "withdrawn - gradual"),
        ("EUR 500 (EA 2016)", 500, 31_700, 0.904, "issuance stopped"),
        ("CAD 1,000 (CA 2000)", 1_000, 35_800, 1.485, "issuance stopped"),
        ("SGD 10,000 (SG 2014)", 10_000, 72_000, 1.267, "issuance stopped"),
        ("MYR 1,000 (MY 1999)", 1_000, 13_100, 3.80, "demonetized"),
        ("CHF 1,000 (CH 2024)", 1_000, 91_000, 0.880, "current"),
        ("SGD 1,000 (SG 2024)", 1_000, 121_000, 1.336, "current"),
        ("EUR 200 (EA 2024)", 200, 43_000, 0.924, "current"),
        ("USD 100 (US 2024)", 100, 85_900, 1.0, "current"),
        ("JPY 10,000 (JP 2024)", 10_000, 4_910_000, 151.5, "current"),
        ("PHP 1,000 (PH 2024)", 1_000, 233_000, 57.3, "current"),
        ("VND 500,000 (VN 2024)", 500_000, 114_000_000, 25_000.0, "current"),
        ("KRW 50,000 (KR 2024)", 50_000, 49_300_000, 1_364.0, "current"),
        ("MYR 100 (MY 2024)", 100, 56_800, 4.57, "current"),
        ("IDR 100,000 (ID 2024)", 100_000, 78_600_000, 15_850.0, "current"),
        ("CNY 100 (CN 2024)", 100, 95_800, 7.19, "current"),
    ],
    columns=["note", "value_lcu", "gdp_pc_lcu", "lcu_per_usd", "status"],
)


def denomination_metrics() -> pd.DataFrame:
    d = DENOMS.copy()
    d["pct_of_gdp_pc"] = 100 * d.value_lcu / d.gdp_pc_lcu
    d["usd_value"] = d.value_lcu / d.lcu_per_usd
    # "days of average income" a single note represents
    d["days_of_income"] = d.value_lcu / (d.gdp_pc_lcu / 365)
    return d.sort_values("pct_of_gdp_pc", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 2. Bulk: what it takes to move 10 million baht
# ---------------------------------------------------------------------------
def bulk_table(amount_thb=10_000_000, thb_per_usd=33.0, usd_per_eur=1.15,
               gold_usd_per_oz=4_000.0) -> pd.DataFrame:
    thick_mm = 0.11  # typical banknote thickness
    rows = []
    # name, face value, width mm, height mm, grams per note (approximate)
    notes = [("THB 1,000", 1_000, 162, 72, 1.00, amount_thb),
             ("THB 500", 500, 156, 72, 0.95, amount_thb),
             ("THB 100", 100, 150, 72, 0.90, amount_thb),
             ("USD 100", 100, 156, 66.3, 1.00, amount_thb / thb_per_usd),
             ("EUR 200", 200, 153, 77, 1.05, amount_thb / thb_per_usd / usd_per_eur)]
    for name, face, w, h, g, amt in notes:
        n = amt / face
        rows.append((name, n, n * g / 1_000, n * w * h * thick_mm / 1e6))
    oz = amount_thb / thb_per_usd / gold_usd_per_oz
    kg = oz * 31.1035 / 1_000
    rows.append(("Gold", np.nan, kg, kg * 1_000 / 19.32 / 1_000))
    rows.append(("USDT stablecoin", np.nan, 0.0, 0.0))
    return pd.DataFrame(rows, columns=["form", "pieces", "kg", "litres"])


# ---------------------------------------------------------------------------
# 3. Logistics & seigniorage of replacing 1,000s (Thailand), Monte Carlo
# ---------------------------------------------------------------------------
def logistics_mc(rng, n=5_000) -> pd.DataFrame:
    U = rng.uniform
    cic = U(1.7e12, 2.1e12, n)          # banknotes in circulation, THB (VERIFY)
    share = U(0.65, 0.80, n)            # value share of 1,000s (VERIFY)
    to500 = U(0.45, 0.65, n)            # demand migrating to 500s
    to100 = U(0.03, 0.08, n)            # ... to 100s
    to_other = U(0.05, 0.25, n)         # ... to gold / FX / crypto (leaks)
    to_dep = 1 - to500 - to100 - to_other  # ... to deposits / e-money
    c500, c100, c1000 = U(1.5, 4.0, n), U(1.2, 3.0, n), U(1.5, 4.0, n)  # THB per note
    l500, l100, l1000 = U(3, 6, n), U(2, 4, n), U(4, 8, n)              # note life, years
    rate = U(0.010, 0.025, n)           # policy-rate proxy for seigniorage
    n_atm, atm_cost = U(40_000, 60_000, n), U(1_000, 10_000, n)
    K = cic * share
    removed = K / 1_000
    add500, add100 = to500 * K / 500, to100 * K / 100
    out = pd.DataFrame({
        "stock_1000_thb": K,
        "notes_removed": removed,
        "notes_added": add500 + add100,
        "one_off_print_thb": add500 * c500 + add100 * c100,
        "annual_print_delta_thb": add500 / l500 * c500 + add100 / l100 * c100 - removed / l1000 * c1000,
        "seigniorage_shift_thb": (to_dep + to_other) * K * rate,
        "seigniorage_leak_abroad_thb": to_other * K * rate,
        "atm_one_off_thb": n_atm * atm_cost,
    })
    return out


# ---------------------------------------------------------------------------
# 4-5. Core model
# ---------------------------------------------------------------------------
HCOLS = ["stock_share", "txn_weight", "bank_access", "digital", "cash_dep"]
# Holder groups of the demonetized notes (honest part sums to 0.90 at the
# reference illicit share of 0.10; rescaled for other illicit shares).
TH_HOLDERS = pd.DataFrame({
    "formal_hh":     [0.32, 0.30, 0.95, 0.85, 0.35],
    "vulnerable_hh": [0.17, 0.20, 0.55, 0.35, 0.80],
    "formal_firm":   [0.08, 0.25, 1.00, 0.90, 0.25],
    "informal_biz":  [0.20, 0.25, 0.60, 0.50, 0.85],
    "cross_border":  [0.05, 0.00, 0.30, 0.20, 0.70],
    "banks_atm":     [0.08, 0.00, 1.00, 1.00, 0.00],
}, index=HCOLS).T
IN_HOLDERS = pd.DataFrame({
    "formal_hh":     [0.20, 0.20, 0.80, 0.30, 0.60],
    "vulnerable_hh": [0.27, 0.30, 0.45, 0.05, 0.95],
    "formal_firm":   [0.08, 0.20, 1.00, 0.50, 0.40],
    "informal_biz":  [0.30, 0.30, 0.55, 0.05, 0.95],
    "cross_border":  [0.02, 0.00, 0.30, 0.10, 0.80],
    "banks_atm":     [0.03, 0.00, 1.00, 1.00, 0.00],
}, index=HCOLS).T
HOLDERS = {"TH": TH_HOLDERS, "IN": IN_HOLDERS}
TAU_DAYS = 4.0  # characteristic conversion time of a fully banked holder


@dataclass
class Scenario:
    key: str
    label: str
    holders: str = "TH"
    share_dem: float = 0.72                 # value share of currency demonetized
    window_days: float = 50                 # time available to convert / exchange
    liquidity_shock: bool = True            # does legal tender disappear at a deadline?
    legal_tender_until_deadline: bool = False
    redeemable_after: bool = False          # late redemption at the central bank allowed?
    r_day: tuple = (0.004, 0.015)           # replacement supply per day (share of stock)
    pre_supply: tuple = (0.0, 0.25)         # replacement ready at day 0
    kyc_bank: tuple = (0.35, 0.65)          # scrutiny intensity at banks (0-1)
    kyc_dealer: tuple = (0.20, 0.40)        # ... at gold / FX / crypto / asset dealers
    fee_struct: tuple = (0.10, 0.30)        # cost of mules / structuring / backdating
    q_struct: tuple = (0.05, 0.15)          # relative detectability of structured deposits
    cap_struct_day: tuple = (0.0005, 0.0030)  # laundering capacity per day, share of TOTAL stock
    struct_days: float | None = None        # default = window_days
    fee_conv: tuple = (0.15, 0.40)          # premium to convert into gold / FX / crypto
    q_conv: tuple = (0.05, 0.15)
    cap_conv_day: tuple = (0.0003, 0.0012)  # conversion capacity per day, share of TOTAL stock
    conv_days: float = 30
    amnesty: bool = True
    amnesty_tax: tuple = (0.50, 0.60)
    illicit_share: tuple = (0.04, 0.20)     # share of demonetized stock held illicitly (UNKNOWN)
    black_frac: tuple = (0.25, 0.60)        # criminal ("black") vs tax-evaded ("grey") money


SCENARIOS = {
    "IN16": Scenario(
        "IN16", "India 2016 (calibration)", holders="IN", share_dem=0.86, window_days=50,
        r_day=(0.004, 0.007), pre_supply=(0.05, 0.20), kyc_bank=(0.25, 0.55), kyc_dealer=(0.10, 0.30),
        fee_struct=(0.15, 0.35), cap_struct_day=(0.0005, 0.0040), illicit_share=(0.02, 0.30)),
    "S1": Scenario("S1", "Shock, 50-day window (India-style)"),
    "S2": Scenario(
        "S2", "Announced, 90-day deadline (Nigeria-style)", window_days=90,
        legal_tender_until_deadline=True, r_day=(0.003, 0.012), pre_supply=(0.05, 0.35),
        kyc_bank=(0.30, 0.60), fee_struct=(0.05, 0.20), cap_struct_day=(0.0005, 0.0025),
        fee_conv=(0.03, 0.10), cap_conv_day=(0.0005, 0.0015), conv_days=90, amnesty=False),
    "S3": Scenario(
        "S3", "Gradual phase-out, 5 years (euro/Canada/Singapore-style)", window_days=1825,
        liquidity_shock=False, legal_tender_until_deadline=True, redeemable_after=True,
        kyc_bank=(0.20, 0.40), kyc_dealer=(0.10, 0.30), fee_struct=(0.00, 0.03), q_struct=(0.02, 0.06),
        cap_struct_day=(0.03 / 365, 0.08 / 365), fee_conv=(0.01, 0.04), q_conv=(0.03, 0.08),
        cap_conv_day=(0.03 / 365, 0.10 / 365), conv_days=1825, amnesty=False),
    "S4": Scenario(
        "S4", "Phase-out + AML package", window_days=1825, liquidity_shock=False,
        legal_tender_until_deadline=True, redeemable_after=True, kyc_bank=(0.50, 0.80),
        kyc_dealer=(0.50, 0.80), fee_struct=(0.03, 0.10), q_struct=(0.05, 0.12),
        cap_struct_day=(0.01 / 365, 0.03 / 365), fee_conv=(0.05, 0.15), q_conv=(0.10, 0.25),
        cap_conv_day=(0.01 / 365, 0.03 / 365), conv_days=1825, amnesty=False),
}


def draw_params(rng, s: Scenario) -> dict:
    U = lambda t: float(rng.uniform(*t))
    p = {k: U(getattr(s, k)) for k in
         ["r_day", "pre_supply", "kyc_bank", "kyc_dealer", "fee_struct", "q_struct",
          "fee_conv", "q_conv", "amnesty_tax", "illicit_share", "black_frac"]}
    p["cap_struct_total"] = U(s.cap_struct_day) * (s.struct_days or s.window_days)
    p["cap_conv_total"] = U(s.cap_conv_day) * s.conv_days
    extra = p["r_day"] * s.window_days if s.legal_tender_until_deadline else 0.0
    p["R0"] = min(1.0, p["pre_supply"] + extra)
    return p


def honest_side(rng, s: Scenario, p: dict, jitter=0.15) -> dict:
    H = HOLDERS[s.holders].copy()
    noise = rng.uniform(1 - jitter, 1 + jitter, size=H[["bank_access", "digital", "cash_dep"]].shape)
    H[["bank_access", "digital", "cash_dep"]] = np.clip(H[["bank_access", "digital", "cash_dep"]] * noise, 0, 1)
    shares = H.stock_share / H.stock_share.sum() * (1 - p["illicit_share"])
    # strict documentation slows low-access holders down
    a_eff = H.bank_access * (1 - 0.5 * p["kyc_bank"] * (1 - H.bank_access))
    conv = 1 - np.exp(-a_eff * s.window_days / TAU_DAYS)
    unconv = shares * (1 - conv)
    lost = 0.0 if s.redeemable_after else float(unconv.sum())
    gap = (1 - p["R0"]) ** 2 / (2 * p["r_day"]) if s.liquidity_shock else 0.0
    contrib = H.txn_weight * H.cash_dep * (1 - H.digital)
    return {
        "gap_days": gap,
        "liq_raw": s.share_dem * float(contrib.sum()) * gap,
        "honest_lost": lost,
        "cross_border_lost": 0.0 if s.redeemable_after else float(unconv["cross_border"]),
        "burden_vulnerable_informal": float((contrib["vulnerable_hh"] + contrib["informal_biz"]) / contrib.sum()),
    }


OPTS = ["deposit", "structure", "convert", "amnesty", "abandon"]


def illicit_side(rng, s: Scenario, p: dict, n=1_500) -> tuple[dict, dict]:
    """Agent-based choice of illicit holders under capacity constraints.

    Holdings x are in units of the scrutiny threshold (lognormal, heavy tail).
    Each agent picks the option with the highest perceived retained value;
    capacity-limited options (structuring, conversion) are filled in random
    order and overflow agents fall back to their next-best option.
    """
    x = rng.lognormal(np.log(0.3), 1.8, n)
    black = rng.random(n) < p["black_frac"]
    pi_eff = np.where(black, rng.uniform(1.5, 3.0, n), rng.uniform(0.6, 0.9, n))  # perceived loss if caught
    pi_cash = np.minimum(pi_eff, 1.0)                                              # what the state collects
    risk = np.exp(rng.normal(0, 0.4, n))
    kb, kd = p["kyc_bank"], p["kyc_dealer"]
    p_dep = np.clip(kb * (1 - np.exp(-x)) * risk, 0, 0.97)
    p_str = np.clip(kb * p["q_struct"] * risk, 0, 0.97)
    p_con = np.clip(kd * p["q_conv"] * risk, 0, 0.97)
    fee_s = np.clip(p["fee_struct"] + rng.normal(0, 0.03, n), 0, 0.9)
    fee_c = np.clip(p["fee_conv"] + rng.normal(0, 0.03, n), 0, 0.9)

    v = np.empty((n, 5))
    v[:, 0] = 1 - p_dep * pi_eff
    v[:, 1] = (1 - fee_s) * (1 - p_str * pi_eff)
    v[:, 2] = (1 - fee_c) * (1 - p_con * pi_eff)
    v[:, 3] = np.where(black | (not s.amnesty), -np.inf, 1 - p["amnesty_tax"])
    v[:, 4] = 0.0
    u = v + rng.gumbel(0, 0.02, v.shape)
    avail = np.isfinite(u)

    share = max(p["illicit_share"], 1e-6)
    cap = {1: p["cap_struct_total"] / share * x.sum(), 2: p["cap_conv_total"] / share * x.sum()}
    assigned = np.full(n, -1)
    order = rng.permutation(n)
    for _ in range(len(OPTS)):
        un = assigned < 0
        if not un.any():
            break
        choice = np.where(avail, u, -np.inf).argmax(axis=1)
        for k in (0, 3, 4):
            assigned[un & (choice == k)] = k
        for k in (1, 2):
            idx = order[(un & (choice == k))[order]]
            if idx.size == 0:
                continue
            ok = np.cumsum(x[idx]) <= cap[k]
            assigned[idx[ok]] = k
            cap[k] -= x[idx[ok]].sum()
            avail[idx[~ok], k] = False

    acc = dict.fromkeys(["extinguished", "captured", "regularized", "laundered", "displaced"], 0.0)
    for k in range(5):
        m = assigned == k
        xs = x[m]
        if k == 0:
            acc["captured"] += (xs * p_dep[m] * pi_cash[m]).sum()
            acc["regularized"] += (xs * p_dep[m] * (1 - pi_cash[m])).sum()
            acc["laundered"] += (xs * (1 - p_dep[m])).sum()
        elif k == 1:
            net = xs * (1 - fee_s[m])
            acc["displaced"] += (xs * fee_s[m]).sum()          # fees stay with launderers
            acc["captured"] += (net * p_str[m] * pi_cash[m]).sum()
            acc["regularized"] += (net * p_str[m] * (1 - pi_cash[m])).sum()
            acc["laundered"] += (net * (1 - p_str[m])).sum()
        elif k == 2:
            acc["captured"] += (xs * p_con[m] * pi_cash[m]).sum()
            acc["regularized"] += (xs * p_con[m] * (1 - pi_cash[m])).sum()
            acc["displaced"] += (xs * (1 - p_con[m])).sum()
        elif k == 3:
            acc["captured"] += (xs * p["amnesty_tax"]).sum()
            acc["regularized"] += (xs * (1 - p["amnesty_tax"])).sum()
        else:
            acc["extinguished"] += xs.sum()
    tot = x.sum()
    acc = {k: v / tot for k, v in acc.items()}
    acc["hit"] = acc["extinguished"] + acc["captured"]
    choices = {OPTS[k]: x[assigned == k].sum() / tot for k in range(5)}
    return acc, choices


def run_once(rng, s: Scenario, p: dict | None = None) -> dict:
    p = p or draw_params(rng, s)
    h = honest_side(rng, s, p)
    il, ch = illicit_side(rng, s, p)
    non_return = p["illicit_share"] * il["extinguished"] + (h["honest_lost"] if not s.redeemable_after else 0.0)
    row = {"scenario": s.key, **p, **h, **il, **{f"ch_{k}": v for k, v in ch.items()},
           "return_rate": 1 - non_return}
    return row


def monte_carlo(rng, s: Scenario, draws: int) -> pd.DataFrame:
    return pd.DataFrame([run_once(rng, s) for _ in range(draws)])


def abc_india(rng, draws=4_000, target=0.993, tol=0.003) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Rejection ABC: keep India draws whose simulated return rate is within
    target +/- tol of the RBI-reported 99.3 % return of demonetized notes."""
    sims = monte_carlo(rng, SCENARIOS["IN16"], draws)
    acc = sims[(sims.return_rate - target).abs() <= tol].copy()
    return sims, acc


def sensitivity_s1(rng, draws=80) -> pd.DataFrame:
    """Hit rate in the Thai shock scenario vs laundering capacity, at 3 scrutiny levels."""
    rows = []
    base = SCENARIOS["S1"]
    for kyc in (0.3, 0.5, 0.8):
        for cap in (0.0002, 0.0005, 0.0010, 0.0015, 0.0020, 0.0030, 0.0040):
            for _ in range(draws):
                p = draw_params(rng, base)
                p["kyc_bank"] = kyc
                p["cap_struct_total"] = cap * base.window_days
                p["illicit_share"] = 0.10
                r = run_once(rng, base, p)
                rows.append({"kyc_bank": kyc, "cap_struct_pct_window": 100 * cap * base.window_days,
                             "hit": r["hit"], "laundered": r["laundered"]})
    return pd.DataFrame(rows).groupby(["kyc_bank", "cap_struct_pct_window"]).median().reset_index()


# ---------------------------------------------------------------------------
# 8. Main
# ---------------------------------------------------------------------------
def q(s, lo=0.25, hi=0.75):
    return float(s.median()), float(s.quantile(lo)), float(s.quantile(hi))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=600)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default="out")
    ap.add_argument("--no-plots", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)

    dm = denomination_metrics()
    dm.to_csv(f"{a.out}/denominations.csv", index=False)
    bulk = bulk_table()
    bulk.to_csv(f"{a.out}/bulk_10m_thb.csv", index=False)
    lg = logistics_mc(rng)
    lg_sum = lg.describe(percentiles=[0.05, 0.5, 0.95]).T[["5%", "50%", "95%"]]
    lg_sum.to_csv(f"{a.out}/logistics_summary.csv")

    sims_in, acc_in = abc_india(rng)
    sims_in.to_csv(f"{a.out}/india_prior_draws.csv", index=False)
    acc_in.to_csv(f"{a.out}/india_abc_accepted.csv", index=False)
    liq_ref = float(sims_in.liq_raw.mean())  # India-2016 = 100

    frames = [monte_carlo(rng, SCENARIOS[k], a.draws) for k in ("S1", "S2", "S3", "S4")]
    # India enters the comparison through its ABC-accepted (calibrated) draws
    india_cal = acc_in.sample(n=min(a.draws, len(acc_in)), random_state=a.seed)
    mc = pd.concat(frames + [india_cal], ignore_index=True)
    mc["liq_index"] = 100 * mc.liq_raw / liq_ref
    mc.to_csv(f"{a.out}/mc_results.csv", index=False)

    summ = []
    for key, g in mc.groupby("scenario"):
        r = {"scenario": key, "label": SCENARIOS[key].label}
        for col in ["liq_index", "hit", "extinguished", "captured", "regularized", "laundered",
                    "displaced", "return_rate", "honest_lost", "cross_border_lost",
                    "burden_vulnerable_informal"]:
            m, lo, hi = q(g[col])
            r[f"{col}_med"], r[f"{col}_p25"], r[f"{col}_p75"] = m, lo, hi
            r[f"{col}_p10"], r[f"{col}_p90"] = float(g[col].quantile(0.10)), float(g[col].quantile(0.90))
            r[f"{col}_mean"] = float(g[col].mean())
        summ.append(r)
    summ = pd.DataFrame(summ)
    summ.to_csv(f"{a.out}/scenario_summary.csv", index=False)

    sens = sensitivity_s1(rng)
    sens.to_csv(f"{a.out}/sensitivity_s1.csv", index=False)

    # India calibration curve: return rate vs illicit share (median over prior draws)
    sims_in["illicit_bin"] = pd.cut(sims_in.illicit_share, bins=np.arange(0.02, 0.32, 0.02))
    calib = sims_in.groupby("illicit_bin", observed=True).agg(
        illicit_mid=("illicit_share", "median"), ret_med=("return_rate", "median"),
        ret_p10=("return_rate", lambda s: s.quantile(0.10)), ret_p90=("return_rate", lambda s: s.quantile(0.90)),
        accept_rate=("return_rate", lambda s: float(((s - 0.993).abs() <= 0.003).mean()))).reset_index(drop=True)
    calib.to_csv(f"{a.out}/india_calibration_curve.csv", index=False)

    # ---- console report
    pd.set_option("display.width", 200, "display.max_columns", 40)
    print("\n=== Relative value of large notes (% of GDP per capita) ===")
    print(dm[["note", "pct_of_gdp_pc", "usd_value", "days_of_income", "status"]].round(3).to_string(index=False))
    print("\n=== Moving 10 million baht ===")
    print(bulk.round(2).to_string(index=False))
    print("\n=== Logistics (THB) 5/50/95 pct ===")
    print((lg_sum / 1e9).round(2).to_string())
    acc_in[["illicit_share", "hit", "extinguished", "captured", "laundered", "displaced", "regularized"]] \
        .describe(percentiles=[.1, .5, .9]).to_csv(f"{a.out}/india_abc_posterior_summary.csv")
    print(f"\n=== India ABC: accepted {len(acc_in)} of {len(sims_in)} draws ===")
    print(acc_in[["illicit_share", "hit", "extinguished", "captured", "laundered", "displaced",
                  "regularized", "cap_struct_total", "return_rate"]].describe(percentiles=[.1, .5, .9]).round(4))
    print("\n=== Scenario summary (medians, IQR) ===")
    cols = ["scenario", "liq_index_med", "liq_index_p25", "liq_index_p75", "hit_med", "hit_p25", "hit_p75",
            "extinguished_med", "captured_med", "regularized_med", "laundered_med", "displaced_med",
            "return_rate_med", "honest_lost_med", "cross_border_lost_med", "burden_vulnerable_informal_med"]
    print(summ[cols].round(4).to_string(index=False))
    print("\n=== Sensitivity S1 (illicit share fixed at 10%) ===")
    print(sens.round(3).to_string(index=False))
    print("\n=== India calibration curve ===")
    print(calib.round(4).to_string(index=False))

    if not a.no_plots:
        make_plots(a.out, dm, bulk, mc, summ, sens, calib)


def make_plots(out, dm, bulk, mc, summ, sens, calib):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    grey, blue = "#9a9a9a", "#2f6db5"
    # Fig 1 relative value
    d = dm.sort_values("pct_of_gdp_pc")
    fig, ax = plt.subplots(figsize=(8, 6.5))
    colors = [blue if n.startswith("THB 1,000") else grey for n in d.note]
    ax.barh(d.note, d.pct_of_gdp_pc, color=colors)
    ax.set_xscale("log")
    ax.set_xlabel("note value as % of GDP per capita (log scale)")
    ax.set_title("THB 1,000 is a mid-sized 'large note' by international standards")
    fig.tight_layout(); fig.savefig(f"{out}/fig1_relative_value.png", dpi=150); plt.close(fig)
    # Fig 2 bulk
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(bulk.form[::-1], bulk.kg[::-1], color=[blue if f == "THB 500" else grey for f in bulk.form[::-1]])
    ax.set_xlabel("kg needed to carry THB 10 million")
    ax.set_title("Dropping the 1,000 only doubles the weight: 10 kg -> 19 kg")
    fig.tight_layout(); fig.savefig(f"{out}/fig2_bulk.png", dpi=150); plt.close(fig)
    # Fig 3 trade-off
    fig, ax = plt.subplots(figsize=(7, 5))
    for _, r in summ.iterrows():
        ax.errorbar(r.liq_index_med, 100 * r.hit_med,
                    xerr=[[r.liq_index_med - r.liq_index_p25], [r.liq_index_p75 - r.liq_index_med]],
                    yerr=[[100 * (r.hit_med - r.hit_p25)], [100 * (r.hit_p75 - r.hit_med)]],
                    fmt="o", color=blue if r.scenario == "S1" else grey, capsize=3)
        ax.annotate(r.scenario, (r.liq_index_med, 100 * r.hit_med), textcoords="offset points", xytext=(6, 6))
    ax.set_xlabel("liquidity disruption index (India 2016 = 100)")
    ax.set_ylabel("illicit cash extinguished or captured (% of illicit stock)")
    ax.set_title("Only the shock design bites - and it bites the economy too")
    fig.tight_layout(); fig.savefig(f"{out}/fig3_tradeoff.png", dpi=150); plt.close(fig)
    # Fig 4 fate of illicit cash
    parts = ["extinguished", "captured", "regularized", "laundered", "displaced"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    left = np.zeros(len(summ))
    shades = ["#1f4e8c", "#2f6db5", "#9fb8d9", "#b5b5b5", "#d9d9d9"]
    for part, c in zip(parts, shades):
        vals = summ[f"{part}_mean"].values
        ax.barh(summ.scenario, vals, left=left, color=c, label=part)
        left += vals
    ax.legend(ncol=5, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, -0.32))
    ax.set_xlabel("share of illicit cash (means across Monte Carlo draws)")
    ax.set_title("Most illicit cash is laundered or displaced, not destroyed")
    fig.tight_layout(); fig.savefig(f"{out}/fig4_illicit_fate.png", dpi=150); plt.close(fig)
    # Fig 5 India calibration
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(100 * calib.illicit_mid, 100 * calib.ret_med, color=blue)
    ax.fill_between(100 * calib.illicit_mid, 100 * calib.ret_p10, 100 * calib.ret_p90, color=blue, alpha=0.15)
    ax.axhline(99.3, color=grey, ls="--"); ax.text(3, 99.35, "RBI: 99.3% returned", color=grey)
    ax.set_xlabel("assumed illicit share of demonetized cash (%)"); ax.set_ylabel("simulated return rate (%)")
    ax.set_title("India's 99.3% return fits small OR large black-cash stocks")
    fig.tight_layout(); fig.savefig(f"{out}/fig5_india_calibration.png", dpi=150); plt.close(fig)
    # Fig 6 sensitivity
    fig, ax = plt.subplots(figsize=(7, 4))
    for kyc, g in sens.groupby("kyc_bank"):
        ax.plot(g.cap_struct_pct_window, 100 * g.hit, marker="o", label=f"bank scrutiny = {kyc}")
    ax.set_xlabel("laundering capacity over the window (% of all demonetized cash)")
    ax.set_ylabel("hit on illicit cash (%)"); ax.legend()
    ax.set_title("Shock scenario: laundering capacity decides the outcome")
    fig.tight_layout(); fig.savefig(f"{out}/fig6_sensitivity_s1.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    main()
