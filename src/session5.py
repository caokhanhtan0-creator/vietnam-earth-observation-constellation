import numpy as np

# -----------------------------------------------------------------------------
# 1. CONSTANTS & GEOMETRY FUNCTIONS
# -----------------------------------------------------------------------------
R_E = 6378.137       # Earth radius in km (WGS84 / Standard)
MU = 398600.4418     # Standard gravitational parameter (km^3/s^2)
OMEGA_E = 7.292115e-5  # Earth rotation rate (rad/s)
SPEED_OF_LIGHT = 299792.458 # km/s

def compute_geometry(h_km, eps_deg):
    """Computes basic coverage geometry parameters."""
    r = R_E + h_km
    eps = np.radians(eps_deg)
    
    # Nadir angle at satellite
    eta = np.arcsin((R_E / r) * np.cos(eps))
    
    # Earth central angle (lambda)
    lam = np.pi / 2 - eps - eta
    
    # Slant range at edge of coverage
    rho = r * (np.sin(lam) / np.cos(eps))
    
    # Footprint radius (km) & coverage fraction f
    footprint_km = R_E * lam
    f_cov = (1 - np.cos(lam)) / 2.0
    
    # Orbital period (seconds)
    T_sec = 2 * np.pi * np.sqrt(r**3 / MU)
    
    # Max access duration per overhead pass (minutes)
    t_access_max = (lam / np.pi) * T_sec / 60.0
    
    # One-way edge latency (ms)
    edge_latency_ms = (rho / SPEED_OF_LIGHT) * 1000.0
    
    return {
        'r': r,
        'lambda_rad': lam,
        'lambda_deg': np.degrees(lam),
        'footprint_km': footprint_km,
        'f_cov': f_cov,
        'T_sec': T_sec,
        't_access_max_min': t_access_max,
        'edge_latency_ms': edge_latency_ms
    }

# -----------------------------------------------------------------------------
# 2. CONSTELLATION PROPAGATION & GRID COVERAGE SIMULATOR
# -----------------------------------------------------------------------------
def generate_walker_constellation(inc_deg, T_sats, P_planes, F_phase, a_km):
    """Generates initial orbital elements for Walker Delta/Star constellation."""
    inc = np.radians(inc_deg)
    sats_per_plane = T_sats // P_planes
    
    delta_RAAN = 2 * np.pi / P_planes  # Delta spacing
    delta_u = 2 * np.pi / sats_per_plane
    delta_phase = F_phase * (2 * np.pi / T_sats)
    
    satellites = []
    for p in range(P_planes):
        raan = p * delta_RAAN
        for s in range(sats_per_plane):
            u0 = s * delta_u + p * delta_phase
            satellites.append({'inc': inc, 'raan0': raan, 'u0': u0, 'a': a_km})
            
    return satellites

def propagate_satellites_ecef(satellites, t_array):
    """Propagates all satellites over time array and converts to ECEF unit vectors."""
    n_times = len(t_array)
    n_sats = len(satellites)
    
    # Matrix of sat unit vectors in ECEF: [n_times, n_sats, 3]
    sat_vecs = np.zeros((n_times, n_sats, 3))
    
    for i, sat in enumerate(satellites):
        n = np.sqrt(MU / sat['a']**3) # Mean motion (rad/s)
        inc = sat['inc']
        
        for j, t in enumerate(t_array):
            u = sat['u0'] + n * t
            raan_eci = sat['raan0'] # Simplified Keplerian
            raan_ecef = raan_eci - OMEGA_E * t
            
            # Position in ECEF unit vector
            x = np.cos(raan_ecef) * np.cos(u) - np.sin(raan_ecef) * np.sin(u) * np.cos(inc)
            y = np.sin(raan_ecef) * np.cos(u) + np.cos(raan_ecef) * np.sin(u) * np.cos(inc)
            z = np.sin(u) * np.sin(inc)
            
            sat_vecs[j, i] = [x, y, z]
            
    return sat_vecs

def create_global_grid(grid_step_deg=5.0):
    """Creates an area-weighted global lat-lon grid with ECEF unit vectors."""
    lats = np.arange(-90 + grid_step_deg/2, 90, grid_step_deg)
    lons = np.arange(-180 + grid_step_deg/2, 180, grid_step_deg)
    
    grid_units = []
    weights = []
    
    for lat in lats:
        lat_rad = np.radians(lat)
        w = np.cos(lat_rad) # Area weight
        for lon in lons:
            lon_rad = np.radians(lon)
            x = np.cos(lat_rad) * np.cos(lon_rad)
            y = np.cos(lat_rad) * np.sin(lon_rad)
            z = np.sin(lat_rad)
            grid_units.append([x, y, z])
            weights.append(w)
            
    return np.array(grid_units), np.array(weights)

def run_simulation(design_name, h_km, inc_deg, T_sats, P_planes, F_phase, eps_deg=10.0, dt_min=2.0):
    """Runs a 24-hour simulation for a specific design architecture."""
    # Geometry calculations
    geo = compute_geometry(h_km, eps_deg)
    
    # Grid setup
    grid_vecs, weights = create_global_grid(grid_step_deg=4.0)
    weights /= np.sum(weights) # Normalize area weights
    n_grid = len(grid_vecs)
    
    # Time vector (24 hours)
    t_array = np.arange(0, 86400, dt_min * 60.0)
    n_times = len(t_array)
    
    # Constellation setup & propagation
    sats = generate_walker_constellation(inc_deg, T_sats, P_planes, F_phase, geo['r'])
    sat_vecs = propagate_satellites_ecef(sats, t_array)
    
    # Threshold for central angle
    cos_lam_thresh = np.cos(geo['lambda_rad'])
    
    # Coverage tracking matrix: [n_times, n_grid] -> True/False
    coverage_matrix = np.zeros((n_times, n_grid), dtype=bool)
    
    for j in range(n_times):
        # Dot product between all sats and all grid points: [n_sats, n_grid]
        dots = np.dot(sat_vecs[j], grid_vecs.T)
        # Point is covered if any sat dot product >= cos(lambda)
        coverage_matrix[j] = np.any(dots >= cos_lam_thresh, axis=0)
        
    # --------------------------------------------------
    # Calculate Figures of Merit (FOM)
    # --------------------------------------------------
    # 1. Percent coverage (Area-weighted 24h average)
    point_coverage = np.mean(coverage_matrix, axis=0)
    percent_coverage = np.sum(point_coverage * weights) * 100.0
    
    # 2. Revisit gaps calculation per grid point
    mean_gaps = []
    max_gaps = []
    
    for g in range(n_grid):
        timeline = coverage_matrix[:, g]
        if np.all(timeline): # Continuously covered
            mean_gaps.append(0.0)
            max_gaps.append(0.0)
        else:
            # Find gap durations
            gap_lengths = []
            curr_gap = 0
            for vis in timeline:
                if not vis:
                    curr_gap += dt_min
                else:
                    if curr_gap > 0:
                        gap_lengths.append(curr_gap)
                        curr_gap = 0
            if curr_gap > 0:
                gap_lengths.append(curr_gap)
                
            if len(gap_lengths) == 0:
                mean_gaps.append(0.0)
                max_gaps.append(0.0)
            else:
                mean_gaps.append(np.mean(gap_lengths))
                max_gaps.append(np.max(gap_lengths))
                
    mean_revisit = np.sum(np.array(mean_gaps) * weights)
    worst_gap = np.max(max_gaps)
    
    return {
        'Design': design_name,
        'Altitude (km)': h_km,
        'Inclination (deg)': inc_deg,
        'Walker': f"{T_sats}/{P_planes}/{F_phase}",
        'Satellites': T_sats,
        'Central Angle (deg)': round(geo['lambda_deg'], 1),
        'Footprint Radius (km)': int(round(geo['footprint_km'], -1)),
        'Coverage (%)': round(percent_coverage, 1),
        'Mean Revisit (min)': round(mean_revisit, 1),
        'Worst Gap (min)': int(round(worst_gap)),
        'Access/pass max (min)': round(geo['t_access_max_min'], 1),
        'Edge Latency (ms)': round(geo['edge_latency_ms'], 1)
    }

# -----------------------------------------------------------------------------
# 3. MAIN EXECUTION (RUNNING DESIGNS A & B)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Simulating Constellation Architectures (24-Hour Global Grid)...\n")
    
    # Run Design A (Low shell: 550 km, 80 deg, 120/10/1)
    res_A = run_simulation("A: Low shell", h_km=550, inc_deg=80, T_sats=120, P_planes=10, F_phase=1)
    
    # Run Design B (Mid shell: 1200 km, 87 deg, 48/8/2)
    res_B = run_simulation("B: Mid shell", h_km=1200, inc_deg=87, T_sats=48, P_planes=8, F_phase=2)
    
    # Print Comparison Table
    headers = list(res_A.keys())
    print(f"{'Metric':<25} | {'Design A (550 km)':<20} | {'Design B (1200 km)':<20}")
    print("-" * 71)
    for k in headers:
        if k == 'Design': continue
        val_a = str(res_A[k])
        val_b = str(res_B[k])
        print(f"{k:<25} | {val_a:<20} | {val_b:<20}")