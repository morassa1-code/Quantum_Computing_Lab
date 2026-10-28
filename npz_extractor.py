import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from pathlib import Path

d = np.load(Path(__file__).parent / "resonator_spectroscopy_data.npz")
freqs, I, Q = d["frequencies"], d["I"], d["Q"]
LO = 8.8e9  

print(d.files)                       # ['frequencies', 'I', 'Q']
print(freqs.shape, I.shape, Q.shape) # expect (10,) for each

amp   = np.sqrt(I**2 + Q**2)
phase = np.unwrap(np.arctan2(Q, I))
rf    = LO + freqs                  # LO + IF

i_max = np.argmax(amp)
rf_max = rf[i_max]
print(f"Amplitude argmax: index {i_max}, RF = {rf_max / 1e9:.6f} GHz, amp = {amp[i_max]:.4g}")

# FWHM of the amplitude peak: width at half height between the baseline (min amp) and the peak,
# with linear interpolation at the two crossings
half = amp.min() + (amp[i_max] - amp.min()) / 2
left = np.where(amp[:i_max] < half)[0]
right = np.where(amp[i_max:] < half)[0]
if left.size and right.size:
    il = left[-1]
    ir = i_max + right[0]
    rf_left = np.interp(half, [amp[il], amp[il + 1]], [rf[il], rf[il + 1]])
    rf_right = np.interp(half, [amp[ir], amp[ir - 1]], [rf[ir], rf[ir - 1]])
    fwhm = rf_right - rf_left
    print(f"Amplitude FWHM: {fwhm:.4g} Hz ({fwhm / 1e6:.3f} MHz)")
else:
    fwhm = None
    print("Amplitude FWHM: half maximum not crossed on both sides of the peak")

# I and Q in their own figure
fig_iq, ax_iq = plt.subplots(figsize=(7, 4))
ax_iq.plot(rf / 1e9, I, "o-", markersize=2, label="I")
ax_iq.plot(rf / 1e9, Q, "o-", markersize=2, label="Q")
ax_iq.set(xlabel="RF frequency (GHz)", ylabel="I, Q (a.u.)")
ax_iq.axvline(rf_max / 1e9, color="r", linestyle="--", label=f"argmax amp: {rf_max / 1e9:.4f} GHz")
ax_iq.legend()
ax_iq.grid(True)
ax_iq.set_xlim((8.95, 9.05))
fig_iq.tight_layout()

fig, ax = plt.subplots(1, 2, figsize=(14, 4))
ax[0].plot(rf / 1e9, amp, "o-", markersize=2)
ax[0].set(xlabel="RF frequency (GHz)", ylabel="Amplitude (a.u.)")
ax[1].plot(rf / 1e9, phase, "o-", markersize=2)
ax[1].set(xlabel="RF frequency (GHz)", ylabel="Phase (rad)")
# phase spans many multiples of pi, so pick a pi-multiple tick step giving ~6 ticks
pi_step = max(1, int(np.ceil((phase.max() - phase.min()) / np.pi / 6)))
ax[1].yaxis.set_major_locator(MultipleLocator(pi_step * np.pi))
ax[1].yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{round(y / np.pi)}π" if round(y / np.pi) else "0"))
ax[0].plot(rf_max / 1e9, amp[i_max], "ro")
if fwhm is not None:
    ax[0].hlines(half, rf_left / 1e9, rf_right / 1e9, color="g", linewidth=2,
                 label=f"FWHM: {fwhm:.4g} Hz")
ax[1].plot(rf_max / 1e9, phase[i_max], "ro")
for a in ax:
    a.axvline(rf_max / 1e9, color="r", linestyle="--", label=f"argmax amp: {rf_max / 1e9:.4f} GHz")
    a.legend()
    a.grid(True)
plt.tight_layout()
plt.show()
