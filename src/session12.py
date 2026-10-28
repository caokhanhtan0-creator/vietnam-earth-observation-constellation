import numpy as np

# ==============================================================================
# 1. CONSTANTS & WGS-84 ENVIRONMENT
# ==============================================================================
R_E = 6378.137             # Earth equatorial radius [km]
MU = 398600.4418           # Gravitational parameter [km^3/s^2]
J2 = 1.08262668e-3         # J2 spherical harmonic
OMEGA_E = 7.292115e-5      # Earth rotation rate [rad/s]

# ==============================================================================
# 2. CONSTELLATION & SIMULATION PARAMETERS (OPTIMAL FOC: WALKER 18/3/1)
# ==============================================================================
ALTITUDE = 500.0                 # Operational altitude [km]
INC_RAD = np.radians(97.402)     # SSO inclination [rad]

TOTAL_SATS = 18                  # Optimal Walker Delta 18/3/1 (FOC)
PLANES = 3                       # 3 orbital planes (120 deg RAAN spacing)
SATS_PER_PLANE = 6               # 6 satellites per plane (60 deg in-plane spacing)
PHASING_F = 1                    # Inter-plane phasing factor F = 1

ELEV_MASK_DEG = 10.0             # Minimum ground elevation mask [deg]
ELEV_MASK_RAD = np.radians(ELEV_MASK_DEG)
ROLL_STEER_DEG = 30.0            # SYS-REQ-05: +/- 30 deg cross-track roll steering

SIM_DURATION_HOURS = 48.0
TIME_STEP_SEC = 30.0

r = R_E + ALTITUDE
n = np.sqrt(MU / r**3)
raan_rate = -1.5 * J2 * (R_E / r)**2 * n * np.cos(INC_RAD)

# --- GEOMETRIC SLANT RANGE DERIVATION (STRICTLY BOUNDED BY ELEV >= 10 DEG) ---
# Mode 2 (Active Roll Steering +/- 30 deg): Reaches the 10-deg elevation horizon mask
# Note: Modeled via a circular Field-of-Regard (FOR) slant-range approximation envelope
sin_eta_steer = (R_E / r) * np.cos(ELEV_MASK_RAD)
eta_steer_rad = np.arcsin(sin_eta_steer)                      # 65.954 deg (Max FOR)
lambda_steer_rad = (np.pi / 2.0) - ELEV_MASK_RAD - eta_steer_rad # 14.046 deg
max_slant_steer = r * np.sin(lambda_steer_rad) / np.cos(ELEV_MASK_RAD) # 1695.09 km

# Mode 1 (Fixed Nadir, Roll = 0 deg): Sensor intrinsic half-FOV without 30-deg roll
eta_nadir_rad = eta_steer_rad - np.radians(ROLL_STEER_DEG)    # 35.954 deg (Fixed FOV)
elev_nadir_rad = np.arccos((r / R_E) * np.sin(eta_nadir_rad)) # 50.716 deg
lambda_nadir_rad = (np.pi / 2.0) - elev_nadir_rad - eta_nadir_rad # 3.33 deg
max_slant_nadir = r * np.sin(lambda_nadir_rad) / np.cos(elev_nadir_rad) # 630.9757 km

# ==============================================================================
# 3. TARGET NODES & VIETNAM COVERAGE GRID (132 NODES)
# ==============================================================================
STRATEGIC_TARGETS = {
    "Hanoi (Capital)":          (21.0285, 105.8542),
    "Da Nang (Central)":        (16.0544, 108.2022),
    "Ho Chi Minh City (South)": (10.8231, 106.6297),
    "Paracel Is. (Hoang Sa)":   (16.5000, 112.0000),
    "Spratly Is. (Truong Sa)":  (8.6500,  111.9200)
}

lat_grid = np.arange(8.5, 24.0, 1.5)
lon_grid = np.arange(102.0, 119.0, 1.5)
grid_nodes = [(lat, lon) for lat in lat_grid for lon in lon_grid]

satellites = []
for p in range(PLANES):
    raan_0 = p * (2.0 * np.pi / PLANES)
    for s in range(SATS_PER_PLANE):
        u_0 = s * (2.0 * np.pi / SATS_PER_PLANE) + p * (PHASING_F * 2.0 * np.pi / TOTAL_SATS)
        satellites.append({
            "plane": p,
            "sat_id": len(satellites) + 1,
            "raan_0": raan_0,
            "u_0": u_0
        })

time_array = np.arange(0.0, SIM_DURATION_HOURS * 3600.0 + TIME_STEP_SEC, TIME_STEP_SEC)
num_steps = len(time_array)

def target_to_ecef(lat_deg, lon_deg):
    phi = np.radians(lat_deg)
    lam = np.radians(lon_deg)
    return np.array([
        R_E * np.cos(phi) * np.cos(lam),
        R_E * np.cos(phi) * np.sin(lam),
        R_E * np.sin(phi)
    ])

target_ecef_dict = {name: target_to_ecef(lat, lon) for name, (lat, lon) in STRATEGIC_TARGETS.items()}
grid_ecef_array = np.array([target_to_ecef(lat, lon) for lat, lon in grid_nodes])

access_nadir_nodes = {name: np.zeros(num_steps, dtype=bool) for name in STRATEGIC_TARGETS}
access_steer_nodes = {name: np.zeros(num_steps, dtype=bool) for name in STRATEGIC_TARGETS}

grid_nadir_counts = np.zeros((len(grid_nodes), num_steps), dtype=bool)
grid_steer_counts = np.zeros((len(grid_nodes), num_steps), dtype=bool)

# ==============================================================================
# 4. ORBIT PROPAGATION LOOP
# ==============================================================================
print(f"Executing dual-mode orbit propagation for Walker {TOTAL_SATS}/{PLANES}/{PHASING_F} over {num_steps} steps...")
print(f"  - Mode 1 (Fixed Nadir, Roll = 0 deg)  : Off-nadir = {np.degrees(eta_nadir_rad):.2f} deg | Elev = {np.degrees(elev_nadir_rad):.2f} deg | Max Slant = {max_slant_nadir:.2f} km")
print(f"  - Mode 2 (Roll Steer +/- 30.0 deg)    : Off-nadir = {np.degrees(eta_steer_rad):.2f} deg | Elev = {ELEV_MASK_DEG:.2f} deg | Max Slant = {max_slant_steer:.2f} km")

cos_i, sin_i = np.cos(INC_RAD), np.sin(INC_RAD)

for step_idx, t_sec in enumerate(time_array):
    theta_gast = OMEGA_E * t_sec
    cos_g, sin_g = np.cos(theta_gast), np.sin(theta_gast)
    R_eci_to_ecef = np.array([
        [ cos_g, sin_g, 0.0],
        [-sin_g, cos_g, 0.0],
        [   0.0,   0.0, 1.0]
    ])
    
    sat_pos_ecef = []
    for sat in satellites:
        u_t = sat["u_0"] + n * t_sec
        raan_t = sat["raan_0"] + raan_rate * t_sec
        r_orb = np.array([r * np.cos(u_t), r * np.sin(u_t), 0.0])
        
        cos_w, sin_w = np.cos(raan_t), np.sin(raan_t)
        R_orb_to_eci = np.array([
            [cos_w, -sin_w * cos_i,  sin_w * sin_i],
            [sin_w,  cos_w * cos_i, -cos_w * sin_i],
            [  0.0,          sin_i,          cos_i]
        ])
        
        r_ecef = R_eci_to_ecef @ (R_orb_to_eci @ r_orb)
        sat_pos_ecef.append(r_ecef)
        
    sat_pos_ecef = np.array(sat_pos_ecef)
    
    for name, r_target in target_ecef_dict.items():
        dist = np.linalg.norm(sat_pos_ecef - r_target, axis=1)
        if np.any(dist <= max_slant_nadir):
            access_nadir_nodes[name][step_idx] = True
        if np.any(dist <= max_slant_steer):
            access_steer_nodes[name][step_idx] = True
            
    diff_grid = grid_ecef_array[:, np.newaxis, :] - sat_pos_ecef[np.newaxis, :, :]
    dist_matrix = np.linalg.norm(diff_grid, axis=2)
    
    grid_nadir_counts[:, step_idx] = np.any(dist_matrix <= max_slant_nadir, axis=1)
    grid_steer_counts[:, step_idx] = np.any(dist_matrix <= max_slant_steer, axis=1)

# ==============================================================================
# 5. FIGURE OF MERIT (FOM) EVALUATION
# ==============================================================================
def analyze_fom(access_mask, dt_sec=30.0):
    diff_mask = np.diff(access_mask.astype(int))
    pass_starts = np.where(diff_mask == 1)[0] + 1
    pass_ends = np.where(diff_mask == -1)[0]
    
    if access_mask[0]:
        pass_starts = np.insert(pass_starts, 0, 0)
    if access_mask[-1]:
        pass_ends = np.append(pass_ends, len(access_mask) - 1)
        
    num_passes = len(pass_starts)
    if num_passes == 0:
        return 0, 0.0, 0.0, 0.0, 0.0
        
    access_durations = (pass_ends - pass_starts + 1) * (dt_sec / 60.0)
    if num_passes > 1:
        gaps = (pass_starts[1:] - pass_ends[:-1] - 1) * (dt_sec / 60.0)
        mean_revisit = np.mean(gaps)
        max_gap = np.max(gaps)
    else:
        mean_revisit = SIM_DURATION_HOURS * 60.0
        max_gap = mean_revisit
        
    coverage_pct = (np.sum(access_mask) / len(access_mask)) * 100.0
    return num_passes, mean_revisit, max_gap, np.mean(access_durations), coverage_pct

print("\n" + "=" * 110)
print("  NUMERICAL SIMULATION RESULTS - OPTIMAL WALKER 18/3/1 (500 km SSO)")
print("=" * 110)
print(f"{'Strategic Target Node':<26} | {'Passes (N/S)':<12} | {'Fixed Nadir Rev':<15} | {'Active Steer Rev':<16} | {'Mean Access':<12} | {'Coverage %'}")
print("-" * 110)

for name in STRATEGIC_TARGETS:
    p_n, mr_n, mg_n, ma_n, c_n = analyze_fom(access_nadir_nodes[name], TIME_STEP_SEC)
    p_s, mr_s, mg_s, ma_s, c_s = analyze_fom(access_steer_nodes[name], TIME_STEP_SEC)
    passes_str = f"{p_n:>2d} / {p_s:<2d}"
    print(f"{name:<26} | {passes_str:<12} | {mr_n:>11.2f} min | {mr_s:>12.2f} min | {ma_s:>8.2f} min | {c_s:>8.2f}%")

grid_nadir_fom = [analyze_fom(grid_nadir_counts[i], TIME_STEP_SEC) for i in range(len(grid_nodes))]
grid_steer_fom = [analyze_fom(grid_steer_counts[i], TIME_STEP_SEC) for i in range(len(grid_nodes))]

avg_p_n  = np.mean([s[0] for s in grid_nadir_fom])
avg_mr_n = np.mean([s[1] for s in grid_nadir_fom])

avg_p_s  = np.mean([s[0] for s in grid_steer_fom])
avg_mr_s = np.mean([s[1] for s in grid_steer_fom])
avg_ma_s = np.mean([s[3] for s in grid_steer_fom])
avg_c_s  = np.mean([s[4] for s in grid_steer_fom])

print("-" * 110)
avg_passes_str = f"{avg_p_n:>4.1f} / {avg_p_s:<4.1f}"
print(f"{'VIETNAM GRID AVG (132)':<26} | {avg_passes_str:<12} | {avg_mr_n:>11.2f} min | {avg_mr_s:>12.2f} min | {avg_ma_s:>8.2f} min | {avg_c_s:>8.2f}%")
print("=" * 110)