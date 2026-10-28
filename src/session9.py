import numpy as np
import matplotlib.pyplot as plt

# Entry & Atmospheric Parameters
ve = 7800.0 # Entry velocity (m/s)
H = 7500.0 # Scale height (m)
rho0 = 1.225 # Sea-level density (kg/m^3)
beta = 300.0 # Ballistic coefficient (kg/m^2)
gamma = np.radians(6) # Flight-path angle (rad)
# Altitude vector from 120 km down to 0 km
h = np.linspace(120e3, 0, 1000)
# Exponential atmospheric density model
rho = rho0 * np.exp(-h / H)
# Allen-Eggers velocity profile
v = ve * np.exp(-(rho0 * H) / (2 * beta * np.sin(gamma)) * np.exp(-h / H))
# Deceleration (g-load)
a_g = (rho * v**2 / (2 * beta)) / 9.81
# Stagnation heating rate (W/cm^2) for Rn = 1.0 m
q_dot = (1.7415e-4 * np.sqrt(rho / 1.0) * v**3) / 1e4
# Peak values and altitudes
idx_peak_a = np.argmax(a_g)
h_peak_a = h[idx_peak_a] / 1000.0
max_a = a_g[idx_peak_a]
idx_peak_q = np.argmax(q_dot)
h_peak_q = h[idx_peak_q] / 1000.0
max_q = q_dot[idx_peak_q]
print(f"Peak Deceleration: {max_a:.2f} g at {h_peak_a:.2f} km altitude")
print(f"Peak Stagnation Heating: {max_q:.2f} W/cm^2 at {h_peak_q:.2f} km altitude")
# Plotting the Entry Profile
fig, ax1 = plt.subplots(figsize=(8, 6))
color = 'tab:red'
ax1.set_xlabel('Deceleration (g)', color=color)
ax1.plot(a_g, h/1000, color=color, linewidth=2, label='Deceleration (g)')
ax1.tick_params(axis='x', labelcolor=color)
ax1.set_ylabel('Altitude (km)')
ax1.set_ylim(0, 90)
ax1.set_xlim(0, 18)
ax1.grid(True, linestyle='--', alpha=0.5)
ax2 = ax1.twiny()
color = 'tab:orange'
ax2.set_xlabel('Stagnation Heating (W/cm²)', color=color)
ax2.plot(q_dot, h/1000, color=color, linewidth=2, linestyle='--', label='Stagnation Heating')
ax2.tick_params(axis='x', labelcolor=color)
plt.title('Entry Profile: Deceleration and Heating vs Altitude\n($\\beta = 300\{ kg/m}^2, \\gamma = 6^\\circ$)')
plt.show()
