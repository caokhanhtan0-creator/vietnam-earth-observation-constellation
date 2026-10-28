import numpy as np
import matplotlib
matplotlib.use('TkAgg') # Tkinter backend
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Physical Constants
MU = 398600         # km^3/s^2
R_E = 6378          # km
J2 = 1.0826e-3      # J2 harmonic coefficient

def j2_eom(t, state):
    rx, ry, rz, vx, vy, vz = state
    r       = np.linalg.norm([rx, ry, rz])
    a_tb    = -MU / (r**3) * np.array([rx, ry, rz])
    z2_r2   = (rz / r)**2
    factor  = 1.5 * J2 * MU * (R_E**2) / (r**5)
    a_j2 = factor * np.array([
        rx * (5 * z2_r2 - 1),
        ry * (5 * z2_r2 - 1),
        rz * (5 * z2_r2 - 3)
    ])
    return [vx, vy, vz, *(a_tb + a_j2)]

def elements_to_state(a, e, inc_deg, raan_deg=0, argp_deg=0, nu_deg=0):
    inc, raan, argp, nu = np.radians([inc_deg, raan_deg, argp_deg, nu_deg])
    p           = a * (1 - e**2)
    r_mag       = p / (1 + e * np.cos(nu))
    r_pqw       = np.array([r_mag * np.cos(nu), r_mag * np.sin(nu), 0.0])
    v_pqw       = np.array([-np.sqrt(MU/p) * np.sin(nu), np.sqrt(MU/p) * (e + np.cos(nu)), 0.0])
    R_z_raan    = np.array([[np.cos(raan), -np.sin(raan), 0], [np.sin(raan), np.cos(raan), 0], [0, 0, 1]])
    R_x_inc     = np.array([[1, 0, 0], [0, np.cos(inc), -np.sin(inc)], [0, np.sin(inc), np.cos(inc)]])
    R_z_argp    = np.array([[np.cos(argp), -np.sin(argp), 0], [np.sin(argp), np.cos(argp), 0], [0, 0, 1]])
    Q           = R_z_raan @ R_x_inc @ R_z_argp
    return Q @ r_pqw, Q @ v_pqw

def state_to_raan(r, v):
    h = np.cross(r, v)
    n = np.cross([0, 0, 1], h)
    return np.arctan2(n[1], n[0])


# ==========================================
# 3. PROPAGATION & ANALYTICAL COMPUTATION
# ==========================================
def run_simulation(inc_deg, a=6798.0, e=0.001, duration_days=3.0):
    """Propagates orbit numerically and computes analytical secular drift."""
    r0, v0 = elements_to_state(a, e, inc_deg)

    t_span = (0, duration_days * 86400)
    t_eval = np.linspace(0, duration_days * 86400, 2000)

    # Integrate equations of motion using DOP853 explicit Runge-Kutta
    sol = solve_ivp(
        j2_eom, t_span, np.concatenate([r0, v0]),
        t_eval=t_eval, rtol=1e-10, atol=1e-12, method='DOP853'
    )

    # Recover RAAN at each step and unwrap phase discontinuities
    raan_rad = [state_to_raan(sol.y[:3, k], sol.y[3:, k]) for k in range(len(sol.t))]
    raan_deg = np.degrees(np.unwrap(raan_rad))

    # Compute numerical slope (deg/day)
    num_slope = (raan_deg[-1] - raan_deg[0]) / duration_days
    
    # Analytical secular rate calculation
    n = np.sqrt(MU / a**3)
    p = a * (1 - e**2)
    sec_rate_rad_s = -1.5 * J2 * (R_E / p)**2 * n * np.cos(np.radians(inc_deg))
    sec_rate_deg_day = np.degrees(sec_rate_rad_s) * 86400
    return sol.t / 86400.0, raan_deg, sec_rate_deg_day * (sol.t / 86400.0), num_slope, sec_rate_deg_day

# Perform simulations
t_days, raan_51_num, raan_51_sec, slope_51_6, secular_51_6 = run_simulation(51.6)
_, raan_98_num, raan_98_sec, slope_98, secular_98 = run_simulation(98.0)

diff_pct = abs(slope_51_6 - secular_51_6) / abs(secular_51_6) * 100

# Plotting
# ==========================================
# 4. PLOTTING & EXPORT
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# i = 51.6 deg Plot
ax1.plot(t_days, raan_51_num, label='Numerical (SciPy DOP853)', color='#1f77b4', linewidth=1.5)
ax1.plot(t_days, raan_51_sec, label='Secular Prediction ($J_2$)', color='#d62728', linestyle='--', linewidth=2)
ax1.set_title('RAAN Drift over 3 Days ($i = 51.6^\\circ$)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Time (Days)')
ax1.set_ylabel('$\Delta\Omega$ - RAAN Change (deg)')
ax1.grid(True, linestyle=':', alpha=0.7)
ax1.legend(loc='best')

# i = 98.0 deg Plot
ax2.plot(t_days, raan_98_num, label='Numerical (SciPy DOP853)', color='#2ca02c', linewidth=1.5)
ax2.plot(t_days, raan_98_sec, label='Secular Prediction ($J_2$)', color='#d62728', linestyle='--', linewidth=2)
ax2.set_title('RAAN Drift over 3 Days ($i = 98.0^\\circ$ - Reverse Drift)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Time (Days)')
ax2.set_ylabel('$\Delta\Omega$ - RAAN Change (deg)')
ax2.grid(True, linestyle=':', alpha=0.7)
ax2.legend(loc='best')

plt.tight_layout()
plt.show()

# ==========================================
# 5. PRINT RESULTS SUMMARY TO TERMINAL
# ==========================================
print(f"=== Results for i = 51.6 deg ===")
print(f"Numerical RAAN Drift: {slope_51_6:.4f} deg/day")
print(f"Analytical Secular Drift: {secular_51_6:.4f} deg/day")
print(f"Percentage Difference: {diff_pct:.2f}%\n")

print(f"=== Results for i = 98.0 deg ===")
print(f"Numerical RAAN Drift: +{slope_98:.4f} deg/day (Precesses Eastward)")
