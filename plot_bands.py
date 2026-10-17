"""Compare the PBE and HSE06 band structures of 2H-MoS2.

Reads:
    2-pbe/vasprun.xml      PBE bands along the KPOINTS_OPT path
    3-hse06/vasprun.xml    HSE06 bands along the same path

Prints the band gap of each run and plots both band structures with the
valence band maximum at 0 eV.

Usage:
    python plot_bands.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from pymatgen.electronic_structure.core import Spin
from pymatgen.io.vasp import Vasprun

HERE = Path(__file__).resolve().parent
RUNS = [("PBE", "2-pbe", "C0", "--"), ("HSE06", "3-hse06", "C3", "-")]


def read_bands(folder):
    """Band structure along the KPOINTS_OPT path."""
    run = Vasprun(HERE / folder / "vasprun.xml", parse_projected_eigen=False)
    return run.get_band_structure(HERE / folder / "KPOINTS_OPT", line_mode=True)


def path_ticks(bs):
    """Positions and labels of the high-symmetry points along the path."""
    ticks, labels = [], []
    for branch in bs.branches:
        for index in (branch["start_index"], branch["end_index"]):
            x = bs.distance[index]
            label = bs.kpoints[index].label.replace("GAMMA", r"$\Gamma$")
            if ticks and abs(x - ticks[-1]) < 1e-6:
                if label not in labels[-1].split("|"):
                    labels[-1] += "|" + label
                continue
            ticks.append(x)
            labels.append(label)
    return ticks, labels


def main():
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for name, folder, color, style in RUNS:
        bs = read_bands(folder)
        gap = bs.get_band_gap()
        kind = "direct" if gap["direct"] else "indirect"
        print(
            f"{name:6s} gap = {gap['energy']:.3f} eV ({kind}, {gap['transition'].replace('GAMMA', 'Γ')})"
        )

        vbm = bs.get_vbm()["energy"]
        energies = bs.bands[Spin.up] - vbm
        # plot each branch separately, so no line is drawn across a path break
        for branch in bs.branches:
            k = slice(branch["start_index"], branch["end_index"] + 1)
            ax.plot(bs.distance[k], energies[:, k].T, color=color, ls=style, lw=0.9)
        ax.plot([], [], color=color, ls=style, label=f"{name}, {gap['energy']:.2f} eV")

    ticks, labels = path_ticks(bs)
    for x in ticks:
        ax.axvline(x, color="0.6", lw=0.5)
    ax.axhline(0, color="0.6", lw=0.5)
    ax.set_xticks(ticks, labels, fontsize=8)
    ax.set_xlim(ticks[0], ticks[-1])
    ax.set_ylim(-4, 4)
    ax.set_ylabel(r"$E - E_\mathrm{VBM}$ (eV)")
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    fig.tight_layout()
    fig.savefig(HERE / "MoS2_PBE_HSE06_bands.png", dpi=300)
    fig.savefig(HERE / "MoS2_PBE_HSE06_bands.pdf")


if __name__ == "__main__":
    main()
