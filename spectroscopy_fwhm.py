import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).parent
# npz files of the resonator spectroscopy runs; falls back to plots/ where the notebook saves them
DATA_DIR = ROOT / "data" / "Experiment_2"
if not DATA_DIR.exists():
    DATA_DIR = ROOT / "plots" / "Experiment_2"
EDGE_FRACTION = 0.1  # fraction of points at each end of the sweep used to estimate the baseline


def amplitude_fwhm(freqs, amp):
    """FWHM of the resonator dip in the amplitude trace.
    base = median of the sweep edges, dip = minimum, half level = midway between them (amplitude, not power).
    Crossings are linearly interpolated. Returns None if the half level isn't crossed on both sides."""
    i_dip = np.argmin(amp)
    n_edge = max(1, int(len(amp) * EDGE_FRACTION))
    base = np.median(np.concatenate([amp[:n_edge], amp[-n_edge:]]))
    dip = amp[i_dip]
    half = (base + dip) / 2
    left = np.where(amp[:i_dip] > half)[0]
    right = np.where(amp[i_dip:] > half)[0]
    if not (left.size and right.size):
        return None
    il = left[-1]
    ir = i_dip + right[0]
    f_left = np.interp(half, [amp[il + 1], amp[il]], [freqs[il + 1], freqs[il]])
    f_right = np.interp(half, [amp[ir - 1], amp[ir]], [freqs[ir - 1], freqs[ir]])
    return dict(i_dip=i_dip, base=base, dip=dip, half=half, f_left=f_left, f_right=f_right, fwhm=f_right - f_left)


def analyze(path):
    d = np.load(path)
    freqs, amp = d["frequencies"], d["IQ_abs"]
    res = amplitude_fwhm(freqs, amp)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(freqs / 1e6, amp, "o-", markersize=2, label="|IQ|")
    ax.set(xlabel="Frequency (MHz)", ylabel="Amplitude (a.u.)", title=path.stem)
    ax.grid(True)
    if res is None:
        print(f"{path.name}: half level not crossed on both sides of the dip")
    else:
        f_dip = freqs[res["i_dip"]]
        ax.axhline(res["base"], color="gray", linestyle="--", label=f"base: {res['base']:.4g}")
        ax.axhline(res["dip"], color="r", linestyle="--", label=f"dip: {res['dip']:.4g} at {f_dip / 1e6:.3f} MHz")
        ax.hlines(res["half"], res["f_left"] / 1e6, res["f_right"] / 1e6, color="orange", linewidth=3,
                  label=f"linewidth (FWHM): {res['fwhm'] / 1e6:.4f} MHz")
        print(f"{path.name}: dip at {f_dip / 1e6:.4f} MHz, base {res['base']:.4g}, dip {res['dip']:.4g}, "
              f"half {res['half']:.4g}, FWHM {res['fwhm'] / 1e6:.4f} MHz")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path.with_name(path.stem + "_fwhm.png"), dpi=150)


files = [Path(p) for p in sys.argv[1:]] or sorted(DATA_DIR.glob("Resonator_Spectroscopy_*.npz"))
if not files:
    sys.exit(f"No spectroscopy npz files found in {DATA_DIR}")
for f in files:
    analyze(f)
plt.show()
