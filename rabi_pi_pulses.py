import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import curve_fit

ROOT = Path(__file__).parent
# same lookup as the other scripts: data/Experiment_2 if present, else where the notebook saves plots
DATA_DIR = ROOT / "data" / "Experiment_2"
if not DATA_DIR.exists():
    DATA_DIR = ROOT / "plots" / "Experiment_2"
MIN_R2 = 0.8        # below this the cosine fit is not trusted and nothing is marked
EDGE_MARGIN = 0.05  # a 2π extremum must lie this far (relative) inside the sweep to count as visible


def cosine(x, offset, amp, period, phase):
    return offset + amp * np.cos(2 * np.pi * x / period + phase)


def fit_rabi(x, y):
    """Fit y = offset + amp*cos(2πx/T + φ), trying many starting periods since the cost is multimodal.
    Returns (params, r2)."""
    best = None
    for period in np.linspace((x[-1] - x[0]) / 6, (x[-1] - x[0]) * 3, 40):
        for phase in (0, np.pi / 2, np.pi, 3 * np.pi / 2):
            try:
                p, _ = curve_fit(cosine, x, y, p0=[y.mean(), (y.max() - y.min()) / 2, period, phase],
                                 maxfev=5000)
            except RuntimeError:
                continue
            res = np.sum((y - cosine(x, *p)) ** 2)
            if p[2] > 0 and p[1] != 0 and (best is None or res < best[0]):
                best = (res, p)
    if best is None:
        return None, 0.0
    res, p = best
    return p, 1 - res / np.sum((y - y.mean()) ** 2)


def pi_pulses(x, p):
    """π and 2π amplitudes from the fitted cosine. The sweep starts in the ground state, i.e. at an extremum
    of the oscillation near x=0; the next extremum (one half period later) is the π pulse and the one after
    that (a full period) the 2π pulse. Extrema closer than a quarter period to zero are the ground state itself.
    The 2π amplitude is None when it falls outside the sweep."""
    offset, amp, period, phase = p
    k = np.arange(-2, 12)
    extrema = (k * np.pi - phase) * period / (2 * np.pi)       # d/dx cos = 0
    extrema = np.sort(extrema[extrema > period / 4 - 1e-12])
    pi_amp, two_pi_amp = extrema[0], extrema[1]
    if pi_amp > x[-1]:
        pi_amp = None
    if two_pi_amp > x[-1] - EDGE_MARGIN * (x[-1] - x[0]):
        two_pi_amp = None
    return pi_amp, two_pi_amp


def analyze(path):
    d = np.load(path)
    x, y = d["amps"], d["IQ_abs"]
    p, r2 = fit_rabi(x, y)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(x, y, "o-", markersize=2, alpha=0.6, label="|IQ|")
    ax.set(xlabel="Drive Amplitude Multiplier", ylabel="|I + iQ| (a.u.)", title=path.stem)
    ax.grid(True, alpha=0.3)

    if p is None or r2 < MIN_R2:
        print(f"{path.name}: no reliable oscillation fit (R^2 = {r2:.2f}), nothing marked")
    else:
        xs = np.linspace(x[0], x[-1], 500)
        ax.plot(xs, cosine(xs, *p), "k", linewidth=1, label=f"cosine fit (R²={r2:.2f})")
        pi_amp, two_pi_amp = pi_pulses(x, p)
        msg = f"{path.name}: R^2 {r2:.2f}, "
        for amp, name, color in ((pi_amp, "pi", "r"), (two_pi_amp, "2pi", "g")):
            if amp is None:
                msg += f"{name} not visible, "
                continue
            ax.axvline(amp, color=color, linestyle="--", label=f"{name.replace('pi', 'π')} pulse: {amp:.3f}")
            msg += f"{name} at {amp:.3f}, "
        print(msg.rstrip(", "))
    ax.legend()
    fig.tight_layout()
    fig.savefig(path.with_name(path.stem + "_pi.png"), dpi=150)


files = [Path(p) for p in sys.argv[1:]] or sorted(DATA_DIR.glob("Power_Rabi*.npz"))
if not files:
    sys.exit(f"No power Rabi npz files found in {DATA_DIR}")
for f in files:
    analyze(f)
plt.show()
