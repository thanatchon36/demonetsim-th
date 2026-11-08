"""Post-processing for DemonetSim-TH.

Computes, from the CSV files written by demonet_sim_th.py:
  * partial rank correlation coefficients (PRCC; Marino et al., 2008) for scenario S1 -> prcc_s1.json
  * bootstrap standard errors of the median bite and disruption index for every scenario
  * prior-versus-posterior summaries of the India 2016 ABC calibration       -> summary_stats.txt

Usage: python model/analysis.py --results results
"""
import argparse
import json
import os

import numpy as np
import pandas as pd

PARAMS = ['illicit_share', 'black_frac', 'kyc_bank', 'kyc_dealer', 'fee_struct', 'q_struct', 'cap_struct_total',
          'fee_conv', 'q_conv', 'cap_conv_total', 'amnesty_tax', 'r_day', 'pre_supply']
OUTCOMES = {'hit': 'hit', 'laund': 'laundered', 'liq': 'liq_index'}


def prcc(df, y, params=PARAMS):
    """PRCC of each parameter with outcome y: correlation of rank residuals after partialling out the others."""
    ranks = df[params + [y]].rank().values
    X, Y = ranks[:, :-1], ranks[:, -1]
    out = {}
    for j, p in enumerate(params):
        Z = np.column_stack([np.ones(len(X)), np.delete(X, j, axis=1)])
        rx = X[:, j] - Z @ np.linalg.lstsq(Z, X[:, j], rcond=None)[0]
        ry = Y - Z @ np.linalg.lstsq(Z, Y, rcond=None)[0]
        out[p] = float(np.corrcoef(rx, ry)[0, 1])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', default='results')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--boot', type=int, default=1000)
    a = ap.parse_args()

    mc = pd.read_csv(os.path.join(a.results, 'mc_results.csv'))
    s1 = mc[mc.scenario == 'S1']
    res = {key: prcc(s1, col) for key, col in OUTCOMES.items()}
    with open(os.path.join(a.results, 'prcc_s1.json'), 'w') as f:
        json.dump(res, f, indent=1)

    lines = ['PRCC, scenario S1 (sorted by absolute value)']
    for key, vals in res.items():
        top = sorted(vals.items(), key=lambda t: -abs(t[1]))[:5]
        lines.append(f'  {key}: ' + ', '.join(f'{p} {v:+.2f}' for p, v in top))

    rng = np.random.default_rng(a.seed)
    lines.append(f'\nMedians with bootstrap standard errors ({a.boot} resamples)')
    for sc, g in mc.groupby('scenario'):
        for col in ['hit', 'liq_index']:
            x = g[col].values
            boot = [np.median(rng.choice(x, len(x))) for _ in range(a.boot)]
            lines.append(f'  {sc:5s} {col:9s} median {np.median(x):8.4f}   SE {np.std(boot):.4f}')

    prior = pd.read_csv(os.path.join(a.results, 'india_prior_draws.csv'))
    acc = pd.read_csv(os.path.join(a.results, 'india_abc_accepted.csv'))
    lines.append(f'\nABC calibration to India 2016: {len(acc)} of {len(prior)} draws accepted '
                 f'({len(acc) / len(prior):.1%})')
    for c in ['illicit_share', 'hit', 'laundered', 'displaced']:
        q = lambda d: ', '.join(f'{v:.3f}' for v in d[c].quantile([.1, .5, .9]))
        lines.append(f'  {c:14s} prior p10/p50/p90 [{q(prior)}]   posterior [{q(acc)}]')

    text = '\n'.join(lines) + '\n'
    with open(os.path.join(a.results, 'summary_stats.txt'), 'w') as f:
        f.write(text)
    print(text)


if __name__ == '__main__':
    main()
