import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).parent
# same lookup as spectroscopy_fwhm.py: data/Experiment_2 if present, else where the notebook saves plots
DATA_DIR = ROOT / "data" / "Experiment_2"
if not DATA_DIR.exists():
    DATA_DIR = ROOT / "plots" / "Experiment_2"
MIN_SNR = 5           # peak height above the noise floor, in units of the noise (MAD) before we call it a peak


def find_f01(freqs, amp):
    """f01 = frequency of the qubit-spectroscopy peak in |IQ|.
    Returns (f01, peak_height, snr); snr = (peak - median) / (1.4826 * MAD) of the trace."""
    i = np.argmax(amp)
    floor = np.median(amp)
    noise = 1.4826 * np.median(np.abs(amp - floor))
    return freqs[i], amp[i], (amp[i] - floor) / noise


def analyze(path):
    d = np.load(path)
    freqs, amp = d["frequencies"], d["IQ_abs"]
    f01, peak, snr = find_f01(freqs, amp)
    found = snr >= MIN_SNR

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(freqs / 1e6, amp, "o-", markersize=2, label="|IQ|")
    if found:
        ax.axvline(f01 / 1e6, color="r", linestyle="--", label=f"f01 offset: {f01 / 1e6:.2f} MHz")
        ax.plot(f01 / 1e6, peak, "ro")
    ax.set(xlabel="Frequency offset (MHz)", ylabel="|I + iQ|", title=path.stem)
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(path.with_name(path.stem + "_f01.png"), dpi=150)
    verdict = f"f01 offset {f01 / 1e6:.2f} MHz" if found else "no clear peak, no line drawn"
    print(f"{path.name}: {verdict} (peak SNR {snr:.1f})")


files = [Path(p) for p in sys.argv[1:]] or sorted(DATA_DIR.glob("Qubit_Spectroscopy_*.npz"))
if not files:
    sys.exit(f"No qubit spectroscopy npz files found in {DATA_DIR}")
for f in files:
    analyze(f)
plt.show()
