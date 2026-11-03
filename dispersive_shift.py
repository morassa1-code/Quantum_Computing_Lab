import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).parent
# same lookup as the other scripts: data/Experiment_2 if present, else where the notebook saves plots
DATA_DIR = ROOT / "data" / "Experiment_2"
if not DATA_DIR.exists():
    DATA_DIR = ROOT / "plots" / "Experiment_2"


def dip_frequency(freqs, mag):
    """Resonator frequency = minimum of the magnitude, refined by a parabola through the 3 points around it."""
    i = np.argmin(mag)
    if 0 < i < len(mag) - 1:
        a, b, _ = np.polyfit(freqs[i - 1:i + 2] - freqs[i], mag[i - 1:i + 2], 2)
        if a > 0:
            return freqs[i] - b / (2 * a)
    return freqs[i]


def analyze(path):
    d = np.load(path)
    off = d["frequency_offset_MHz"]
    f0 = dip_frequency(off, d["magnitude_ground"])
    f1 = dip_frequency(off, d["magnitude_excited"])
    diff = f1 - f0  # = 2*chi, same sign convention as the notebook title
    print(f"{path.name}: f0 = {f0:.3f} MHz, f1 = {f1:.3f} MHz (offsets), f1 - f0 = {diff:.3f} MHz "
          f"(notebook 2chi: {d['two_chi_Hz'] / 1e6:.3f} MHz)")

    fig, (ax_m, ax_p) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    for ax, key, ylabel in ((ax_m, "magnitude", "|I + iQ| (a.u.)"), (ax_p, "phase", "Phase (rad)")):
        ax.plot(off, d[f"{key}_ground"], ".-", label="|0⟩")
        ax.plot(off, d[f"{key}_excited"], ".-", label="|1⟩")
        ax.axvline(f0, color="C0", linestyle="--", alpha=0.8, label=f"f0 = {f0:.2f} MHz")
        ax.axvline(f1, color="C1", linestyle="--", alpha=0.8, label=f"f1 = {f1:.2f} MHz")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend()
    # double arrow between the two dips, showing the difference
    y = d["magnitude_ground"].min() + 0.5 * (d["magnitude_ground"].max() - d["magnitude_ground"].min())
    ax_m.annotate("", xy=(f1, y), xytext=(f0, y), arrowprops=dict(arrowstyle="<->", color="k"))
    ax_m.text((f0 + f1) / 2, y, f"f1 − f0 = {diff:.3f} MHz", ha="center", va="bottom")
    ax_p.set_xlabel("Resonator frequency offset (MHz)")
    fig.suptitle(f"Dispersive shift: f1 − f0 = {diff:.3f} MHz")
    fig.tight_layout()
    fig.savefig(path.with_name(path.stem + "_f0f1.png"), dpi=150)


files = [Path(p) for p in sys.argv[1:]] or sorted(DATA_DIR.glob("Dispersive_Shift_*.npz"))
if not files:
    sys.exit(f"No dispersive shift npz files found in {DATA_DIR}")
for f in files:
    analyze(f)
plt.show()
