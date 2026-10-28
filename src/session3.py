import numpy as np

# ==========================================
# CONSTANTS & PHYSICAL PARAMETERS
# ==========================================
MU = 398600 # Earth gravitational parameter (km^3/s^2)
R_E = 6378 # Earth equatorial radius (km)

def hohmann_transfer(r1, r2):
    """Calculates Hohmann transfer delta-v components and transfer duration."""
    v1 = np.sqrt(MU / r1)
    v2 = np.sqrt(MU / r2)
    a_trans = (r1 + r2) / 2.0

    v_trans_peri = np.sqrt(MU * (2.0 / r1 - 1.0 / a_trans))
    v_trans_apo = np.sqrt(MU * (2.0 / r2 - 1.0 / a_trans))

    dv1 = v_trans_peri - v1
    dv2 = v2 - v_trans_apo
    dv_total = dv1 + dv2
    t_trans_hrs = (np.pi * np.sqrt(a_trans**3 / MU)) / 3600.0

    return dv1, dv2, dv_total, t_trans_hrs, v_trans_apo, v2

# ==========================================
# TASK 2: HOHMANN TRANSFERS
# ==========================================
print("--- TASK 2: HOHMANN TRANSFERS ---")

# Task 2.1: LEO (500 km) to GEO
r1_500 = R_E + 500.0
r2_geo = 42164.14
dv1_geo, dv2_geo, dv_tot_geo, t_geo, v_trans_apo_geo, v_geo = hohmann_transfer(r1_500, r2_geo)

print(f"[LEO 500km -> GEO]")
print(f" dv1: {dv1_geo:.2f} km/s | dv2: {dv2_geo:.2f} km/s | Total dv: {dv_tot_geo:.2f} km/s")
print(f" Transfer Time: {t_geo:.2f} hours\n")

# Task 2.2: LEO (400 km) to MEO (20,200 km altitude)
r1_400 = R_E + 400.0
r2_meo = R_E + 20200.0
dv1_meo, dv2_meo, dv_tot_meo, t_meo, _, _ = hohmann_transfer(r1_400, r2_meo)

print(f"[LEO 400km -> MEO 20,200km]")
print(f" dv1: {dv1_meo:.2f} km/s | dv2: {dv2_meo:.2f} km/s | Total dv: {dv_tot_meo:.2f} km/s")
print(f" Transfer Time: {t_meo:.2f} hours\n")

# ==========================================
# TASK 3: BI-ELLIPTIC COMPARISON (R = 20, r_b = 40*r1)
# ==========================================
print("--- TASK 3: BI-ELLIPTIC VS HOHMANN (R = 20) ---")

r1_norm = 1.0
r2_norm = 20.0
rb_norm = 40.0
v1_phys = np.sqrt(MU / r1_500)

# Hohmann for R = 20
a_h = (r1_norm + r2_norm) / 2.0
v_tp1_h = np.sqrt(2.0/r1_norm - 1.0/a_h)
v_tp2_h = np.sqrt(2.0/r2_norm - 1.0/a_h)
v2_h = np.sqrt(1.0/r2_norm)

dv_h_tot = (v_tp1_h - 1.0) + (v2_h - v_tp2_h)
dv_h_phys = dv_h_tot * v1_phys

# Bi-elliptic for R = 20, r_b = 40
a1_b = (r1_norm + rb_norm) / 2.0
v_tp1_b = np.sqrt(2.0/r1_norm - 1.0/a1_b)
v_tpb1 = np.sqrt(2.0/rb_norm - 1.0/a1_b)

a2_b = (r2_norm + rb_norm) / 2.0
v_tpb2 = np.sqrt(2.0/rb_norm - 1.0/a2_b)
v_tp2_b = np.sqrt(2.0/r2_norm - 1.0/a2_b)

dv_bi_tot = abs(v_tp1_b - 1.0) + abs(v_tpb2 - v_tpb1) + abs(v2_h - v_tp2_b)
dv_bi_phys = dv_bi_tot * v1_phys

print(f"Hohmann Total (R=20): {dv_h_phys:.2f} km/s")
print(f"Bi-elliptic Total (r_b=40): {dv_bi_phys:.2f} km/s")
print(f"Delta-v Savings: {dv_h_phys - dv_bi_phys:.2f} km/s (Bi-elliptic wins)\n")

# ==========================================
# TASK 4: COMBINED BURN (LEO 500km -> GEO with i = 51.6 deg)
# ==========================================
print("--- TASK 4: COMBINED APOGEE BURN ---")

inc_deg = 51.6
inc_rad = np.radians(inc_deg)

# Combined Vector Burn via Law of Cosines
dv_combined = np.sqrt(v_trans_apo_geo**2 + v_geo**2 - 2.0 * v_trans_apo_geo * v_geo * np.cos(inc_rad))

# Separate In-Plane Burn + Plane Change
dv_plane_only = 2.0 * v_geo * np.sin(inc_rad / 2.0)
dv_separate = dv2_geo + dv_plane_only

print(f"Combined Apogee Burn Cost: {dv_combined:.2f} km/s")
print(f"Separate Burns Cost: {dv_separate:.2f} km/s")
print(f"Savings via Vector Combined Burn: {dv_separate - dv_combined:.2f} km/s")