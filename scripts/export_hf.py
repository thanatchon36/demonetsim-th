"""Assemble the Hugging Face dataset thanatchon36/demonetsim-th in build/hf/ and, with --push, upload it.

Contents: every file in results/ (seed 7), the model's input tables exported from model/demonet_sim_th.py
(scenario priors and holder groups), the dataset card scripts/hf_card.md, a CC BY 4.0 LICENSE and SHA256SUMS.

Usage: python scripts/export_hf.py [--push]
"""
import argparse
import dataclasses
import hashlib
import shutil
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "hf"
REPO = "thanatchon36/demonetsim-th"
sys.path.insert(0, str(ROOT / "model"))

from demonet_sim_th import HOLDERS, SCENARIOS, TAU_DAYS  # noqa: E402

CC_BY = """The DemonetSim-TH dataset (thanatchon36/demonetsim-th) is released under the Creative Commons Attribution 4.0
International License (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/

Copyright (c) 2026 Thanatchon Chongmankhong

You are free to share and adapt the material for any purpose, even commercially, provided you give appropriate
credit, provide a link to the license, and indicate if changes were made. The code that produced it is MIT
licensed: https://github.com/thanatchon36/demonetsim-th
"""


def scenarios() -> pd.DataFrame:
    rows = []
    for s in SCENARIOS.values():
        row = {}
        for k, v in dataclasses.asdict(s).items():
            if isinstance(v, tuple):
                row[f"{k}_lo"], row[f"{k}_hi"] = v
            else:
                row[k] = v
        rows.append(row)
    return pd.DataFrame(rows)


def holders() -> pd.DataFrame:
    frames = [h.rename_axis("group").reset_index().assign(country=c) for c, h in HOLDERS.items()]
    out = pd.concat(frames, ignore_index=True)
    out["tau_days"] = TAU_DAYS
    return out[["country", "group", *HOLDERS["TH"].columns, "tau_days"]]


def build() -> Path:
    shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "inputs").mkdir(parents=True)
    shutil.copytree(ROOT / "results", OUT / "results")
    scenarios().to_csv(OUT / "inputs" / "scenarios.csv", index=False)
    holders().to_csv(OUT / "inputs" / "holders.csv", index=False)
    shutil.copyfile(ROOT / "scripts" / "hf_card.md", OUT / "README.md")
    (OUT / "LICENSE").write_text(CC_BY, encoding="utf-8")
    files = sorted(p for p in OUT.rglob("*") if p.is_file() and p.name not in {"SHA256SUMS"})
    sums = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT).as_posix()}" for p in files
            if p.name not in {"README.md"}]
    (OUT / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    return OUT


def push() -> None:
    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(REPO, repo_type="dataset", exist_ok=True)
    api.upload_folder(folder_path=str(OUT), repo_id=REPO, repo_type="dataset",
                      commit_message="Upload DemonetSim-TH results and model inputs (seed 7)")
    print(f"https://huggingface.co/datasets/{REPO}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    print(build())
    if a.push:
        push()
