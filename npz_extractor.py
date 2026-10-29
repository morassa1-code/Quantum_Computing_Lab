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

# FWHM of the power (amp**2) peak: width at half height between the baseline (min power) and the peak,
# with linear interpolation at the two crossings; the a.u. scale cancels since the level is a fraction of the peak
power = amp**2
half_p = power.min() + (power[i_max] - power.min()) / 2
left_p = np.where(power[:i_max] < half_p)[0]
right_p = np.where(power[i_max:] < half_p)[0]
if left_p.size and right_p.size:
    il = left_p[-1]
    ir = i_max + right_p[0]
    rf_left_p = np.interp(half_p, [power[il], power[il + 1]], [rf[il], rf[il + 1]])
    rf_right_p = np.interp(half_p, [power[ir], power[ir - 1]], [rf[ir], rf[ir - 1]])
    fwhm_p = rf_right_p - rf_left_p
    print(f"Power half-max level: {half_p:.4g} (baseline {power.min():.4g}, peak {power[i_max]:.4g})")
    print(f"Power crossings: {rf_left_p:.1f} Hz and {rf_right_p:.1f} Hz")
    print(f"Power FWHM: {fwhm_p / 1e9:.6f} GHz, Q = f0/FWHM = {rf_max / fwhm_p:.0f}")
else:
    fwhm_p = None
    print("Power FWHM: half maximum not crossed on both sides of the peak")

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
# ax[1].set_xlim([8.99, 9.008]) #better resolution for the phase plot
# phase spans many multiples of pi, so pick a pi-multiple tick step giving ~6 ticks
pi_step = max(1, int(np.ceil((phase.max() - phase.min()) / np.pi / 6)))
ax[1].yaxis.set_major_locator(MultipleLocator(pi_step * np.pi))
ax[1].yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{round(y / np.pi)}π" if round(y / np.pi) else "0"))
ax[0].plot(rf_max / 1e9, amp[i_max], "ro")
if fwhm_p is not None:
    ax[0].hlines(np.sqrt(half_p), rf_left_p / 1e9, rf_right_p / 1e9, color="orange", linewidth=2,
                 label=f"Power FWHM: {fwhm_p / 1e9:.6f} GHz")
ax[1].plot(rf_max / 1e9, phase[i_max], "ro")
for a in ax:
    a.axvline(rf_max / 1e9, color="r", linestyle="--", label=f"argmax amp: {rf_max / 1e9:.4f} GHz")
    a.legend()
    a.grid(True)
plt.tight_layout()
plt.show()
