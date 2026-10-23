import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

d = np.load(Path(__file__).parent / "resonator_spectroscopy_data.npz")
freqs, I, Q = d["frequencies"], d["I"], d["Q"]
LO = 5e9  

print(d.files)                       # ['frequencies', 'I', 'Q']
print(freqs.shape, I.shape, Q.shape) # expect (10,) for each

amp   = np.sqrt(I**2 + Q**2)
phase = np.unwrap(np.arctan2(Q, I))
rf    = LO + freqs                  # LO + IF

fig, ax = plt.subplots(1, 2, figsize=(14, 4))
# ax[0].plot(rf / 1e9, I, "o-", label="I")
# ax[0].plot(rf / 1e9, Q, "o-", label="Q")
# ax[0].set(xlabel="RF frequency (GHz)", ylabel="I, Q (a.u.)")
# ax[0].legend()
ax[0].plot(rf / 1e9, 10*np.log10(amp), "o-")
ax[0].set(xlabel="RF frequency (GHz)", ylabel="Amplitude (dB)")
ax[1].plot(rf / 1e9, phase, "o-")
ax[1].set(xlabel="RF frequency (GHz)", ylabel="Phase (rad)")
for a in ax:
    a.grid(True)
plt.tight_layout()
plt.show()
