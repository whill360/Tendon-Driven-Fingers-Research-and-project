"""Entry point for feasible torque set analysis.

Usage:
    python main.py                          # run all presets, plot all
    python main.py vc2007 vc2007_lu         # run specific presets
    python main.py --list                   # list available presets
    python main.py --no-show                # save figures only, don't open windows

Figures are always saved to ./output/.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib

from experiments import PRESETS
from torque_space import compute_feasible_set, compare, FeasibleTorqueSet
from visualize import (
    plot_comparison, plot_overlay, plot_feasible_set, plot_octant_summary,
    plot_dual_focus,
)


OUTPUT_DIR = Path(__file__).parent / "output"


def parse_args(argv):
    show = True
    names = []
    for a in argv:
        if a == "--list":
            print("Available presets:")
            for k in PRESETS:
                print(f"  {k}")
            sys.exit(0)
        elif a == "--no-show":
            show = False
        elif a.startswith("--"):
            print(f"Unknown flag: {a}")
            sys.exit(2)
        else:
            names.append(a)
    if not names:
        names = list(PRESETS.keys())
    return names, show


def main(argv):
    names, show = parse_args(argv)
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sets = []
    for name in names:
        if name not in PRESETS:
            print(f"Unknown preset {name!r}; try --list")
            continue
        result = PRESETS[name]()
        if isinstance(result, FeasibleTorqueSet):
            fts = result
        else:
            fts = compute_feasible_set(result)
        sets.append(fts)
        print(fts.summary())

    if not sets:
        return

    print()
    for line in compare(*sets).items():
        print(f"  {line}")

    if len(sets) == 1:
        fig = plt.figure(figsize=(8, 7))
        ax = fig.add_subplot(111, projection="3d")
        plot_feasible_set(sets[0], ax=ax)
        out = OUTPUT_DIR / f"{sets[0].network_name.replace(' ', '_')}.png"
        fig.savefig(out, dpi=140, bbox_inches="tight")
        print(f"\nsaved {out}")
    else:
        fig_ovl, _ = plot_overlay(*sets)
        ovl_out = OUTPUT_DIR / "overlay.png"
        fig_ovl.savefig(ovl_out, dpi=140, bbox_inches="tight")
        print(f"\nsaved {ovl_out}")

        if len(sets) >= 2:
            fig_dual, _ = plot_dual_focus(*sets)
            dual_out = OUTPUT_DIR / "dual_focus.png"
            fig_dual.savefig(dual_out, dpi=140, bbox_inches="tight")
            print(f"saved {dual_out}")

    if show:
        plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])
