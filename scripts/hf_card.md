---
license: cc-by-4.0
pretty_name: "DemonetSim-TH: simulated demonetization of Thailand's 1,000-baht note"
language:
  - en
  - th
size_categories:
  - 1K<n<10K
task_categories:
  - tabular-regression
tags:
  - demonetization
  - money-laundering
  - agent-based-model
  - approximate-bayesian-computation
  - monte-carlo
  - thailand
  - india
  - banknotes
  - simulation
configs:
  - config_name: monte_carlo
    data_files: results/mc_results.csv
    default: true
  - config_name: scenario_summary
    data_files: results/scenario_summary.csv
  - config_name: india_prior_draws
    data_files: results/india_prior_draws.csv
  - config_name: india_abc_accepted
    data_files: results/india_abc_accepted.csv
  - config_name: denominations
    data_files: results/denominations.csv
  - config_name: scenarios
    data_files: inputs/scenarios.csv
  - config_name: holders
    data_files: inputs/holders.csv
---

# DemonetSim-TH: simulated demonetization of Thailand's 1,000-baht note

> **Every row is a simulation.** The model's inputs are approximations compiled without access to live sources and
> parameter ranges that are assumptions. The outputs describe the model, not Thailand: verify the inputs against
> primary sources, in particular Bank of Thailand banknote statistics, before citing them or using them for policy.

Data for the preprint *Can Demonetization Defeat Grey Capital? Evidence, a Calibrated Agent-Based Model, and a
Research Agenda for Retiring Thailand's 1,000-Baht Note* by Thanatchon Chongmankhong
([read online](https://thanatchon36.github.io/demonetsim-th/paper/) ·
[PDF](https://github.com/thanatchon36/demonetsim-th/blob/main/paper/pdf/paper_en.pdf) ·
[ฉบับภาษาไทย](https://github.com/thanatchon36/demonetsim-th/blob/main/paper/pdf/paper_th.pdf), ธนัชชนม์ จงมั่นคง).
DemonetSim-TH is an agent-based model in which illicit holders choose among deposit, structuring through money
mules, conversion into gold, FX or crypto, amnesty and abandonment under capacity-constrained laundering, while
honest holders face a liquidity gap governed by replacement logistics. It is calibrated to India's 2016
demonetization by rejection ABC on the 99.3% return rate. Code: <https://github.com/thanatchon36/demonetsim-th>;
archived on Zenodo: [10.5281/zenodo.24050061](https://doi.org/10.5281/zenodo.24050061).

*Independent personal research. Does not represent the views of any employer or institution.*

## Files

| path | content |
|---|---|
| `results/mc_results.csv` | Monte Carlo draws: 600 for each Thai scenario S1–S4 and 600 ABC-accepted India draws (IN16), 3,000 rows. Each row holds the sampled parameters, the honest-side outcomes, the fate of illicit cash, the channel choices and the return rate |
| `results/scenario_summary.csv` | per scenario: median, 25th/75th and 10th/90th percentiles and mean of the disruption index, the bite and each fate of illicit cash |
| `results/india_prior_draws.csv` | 4,000 draws from the India 2016 prior, same columns as `mc_results.csv` without `liq_index` |
| `results/india_abc_accepted.csv` | the 1,214 prior draws whose simulated return rate is within 99.3% ± 0.3 pp |
| `results/india_abc_posterior_summary.csv` | count, mean, standard deviation and percentiles of the accepted draws |
| `results/india_calibration_curve.csv` | simulated return rate against the illicit share (2-pp bins): median, 10th and 90th percentiles and the ABC acceptance rate |
| `results/sensitivity_s1.csv` | median bite and laundered share in S1 at an illicit share of 10%, by bank scrutiny (0.3, 0.5, 0.8) and laundering capacity (% of the stock over the 50-day window); 80 draws per cell |
| `results/prcc_s1.json` | partial rank correlation coefficients of 13 parameters with the bite (`hit`), the laundered share (`laund`) and the disruption index (`liq`), scenario S1 |
| `results/summary_stats.txt` | PRCC ranking, bootstrap standard errors of the medians (1,000 resamples) and ABC prior/posterior percentiles |
| `results/denominations.csv` | 19 large banknotes: face value, GDP per capita and exchange rate (approximate), status, value as % of GDP per capita, USD value and days of average income |
| `results/bulk_10m_thb.csv` | number of pieces, weight (kg) and volume (litres) of THB 10 million in five banknotes, gold and a stablecoin |
| `results/logistics_summary.csv` | 5th, 50th and 95th percentiles (THB) of the stock of 1,000s, notes removed and added, printing costs, seigniorage shift and leakage, and ATM conversion cost |
| `results/fig*.png` | the six diagnostic plots written by the model |
| `inputs/scenarios.csv` | the scenario definitions: design flags and the lower (`_lo`) and upper (`_hi`) bounds of every uniform prior |
| `inputs/holders.csv` | the six holder groups for Thailand (TH) and India (IN): share of the demonetized stock, transaction weight, bank access, digital readiness, cash dependence, and the conversion time constant |
| `SHA256SUMS` | checksums of every file above |

## Columns of the simulation draws

Parameters (sampled per draw): `r_day` replacement currency per day and `pre_supply` replacement ready at day 0
(shares of the stock), `R0` share replaced when legal tender lapses, `kyc_bank` and `kyc_dealer` scrutiny at banks
and at gold, FX and crypto dealers (0–1), `fee_struct` and `fee_conv` cost of structuring and of conversion,
`q_struct` and `q_conv` relative detectability, `cap_struct_total` and `cap_conv_total` laundering and conversion
capacity (shares of the total stock), `amnesty_tax`, `illicit_share` share of the demonetized stock held illicitly,
`black_frac` share of illicit holders with criminal rather than tax-evaded money.

Outcomes: `gap_days` liquidity gap, `liq_raw` disruption and `liq_index` the same indexed to the mean India prior
draw (= 100); `honest_lost` and `cross_border_lost` honest wealth not converted (shares of the stock);
`burden_vulnerable_informal` share of disruption borne by vulnerable households and informal businesses. The fate of
illicit cash, as shares of the illicit stock summing to one: `extinguished` (abandoned), `captured` (seized, taxed or
fined), `regularized` (kept after a penalty), `laundered` (entered banks undetected) and `displaced` (moved into
other stores of value or paid as fees); `hit` = extinguished + captured is the bite. `ch_*` are the value shares of
the channel each agent ended in, and `return_rate` the share of demonetized value returned.

Scenarios: IN16 India 2016 (calibration), S1 shock with a 50-day window, S2 announced 90-day deadline, S3 five-year
phase-out, S4 phase-out with an anti-money-laundering package.

## Reproducing

```bash
git clone https://github.com/thanatchon36/demonetsim-th && cd demonetsim-th
make setup && make simulate analysis      # seed 7, 600 draws per scenario
python scripts/export_hf.py               # rebuilds this dataset in build/hf/
```

## Licence

CC BY 4.0 (`LICENSE`). The code that produced the data is MIT licensed.

## Citation

```bibtex
@misc{chongmankhong2026demonetization,
  author = {Chongmankhong, Thanatchon},
  title  = {Can Demonetization Defeat Grey Capital? Evidence, a Calibrated Agent-Based Model,
            and a Research Agenda for Retiring {Thailand}'s 1,000-Baht Note},
  year   = {2026},
  doi    = {10.5281/zenodo.24050061},
  url    = {https://thanatchon36.github.io/demonetsim-th/paper/},
  note   = {Preprint}
}
```
