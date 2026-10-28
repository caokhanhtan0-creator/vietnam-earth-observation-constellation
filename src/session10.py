import numpy as np
from scipy.optimize import minimize_scalar

# Constants
mu = 398600.4418        # Earth gravitational parameter (km^3/s^2)
Re = 6378.137           # Earth equatorial radius (km)

# Orbit Parameters
r1 = Re + 185.0         # LEO radius (km)
r2 = 42164.0            # GEO radius (km)
di = np.radians(51.6)   # Total plane change angle (rad)

# Orbital Velocities
a_t = (r1 + r2) / 2.0
vleo = np.sqrt(mu / r1)
vp = np.sqrt(mu * (2.0 / r1 - 1.0 / a_t))
va = np.sqrt(mu * (2.0 / r2 - 1.0 / a_t))
vgeo = np.sqrt(mu / r2)

# Objective Function: Total Delta-v
def total_dv(f):
    # f = fraction of plane change performed at perigee
    dv1 = np.sqrt(vleo**2 + vp**2 - 2.0 * vleo * vp * np.cos(f * di))
    dv2 = np.sqrt(va**2 + vgeo**2 - 2.0 * va * vgeo * np.cos((1.0 - f) * di))
    return dv1 + dv2

# Optimization Execution
res = minimize_scalar(total_dv, bounds=(0, 1), method='bounded')

# Baseline calculation: 100% plane change at apogee (f = 0)
dv_apogee = total_dv(0.0)

# Print Detailed Results
print("--- TASK 2 NUMERICAL CONFIRMATION ---")
print(f"Optimal fraction at perigee: {res.x * 100:.2f}%")
print(f"Minimum total delta-v: {res.fun:.4f} km/s")
print(f"All-at-apogee delta-v: {dv_apogee:.4f} km/s")
print(f"Delta-v savings: {(dv_apogee - res.fun) * 1000.0:.2f} m/s")
