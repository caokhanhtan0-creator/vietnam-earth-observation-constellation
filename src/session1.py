import numpy as np
from astropy import units as u
from astropy.constants import R_earth
from poliastro.bodies import Earth
from poliastro.twobody import Orbit

# Overriding Earth.k with course reference constants for exact matching
# R_E = 6,378 km, mu = 398,600 km^3/s^2
MU_EARTH = 398600.0 * (u.km**3 / u.s**2)
R_E = 6378.0 * u.km

# =====================================================================
# PART 1: REPRODUCE ALL THREE WORKED EXAMPLES
# =====================================================================

print("--- WORKED EXAMPLE 1: Period of LEO (ISS Altitude, 420 km) ---")
h1 = 420.0 * u.km
a1 = R_E + h1 # 6,798 km

# Orbit creation using poliastro
orb1 = Orbit.from_classical(
    Earth,
    a=a1,
    ecc=0.0 * u.one,
    inc=0.0 * u.deg,
    raan=0.0 * u.deg,
    argp=0.0 * u.deg,
    nu=0.0 * u.deg,
)

# Period using Kepler's Third Law: T = 2*pi*sqrt(a^3 / mu)
T1 = 2 * np.pi * np.sqrt(a1**3 / MU_EARTH)
v1 = np.sqrt(MU_EARTH / a1)

print(f"Semi-major axis (a): {a1:.0f}")
print(f"Orbital Period (T): {T1.to(u.s):.1f} ({T1.to(u.min):.2f})")
print(f"Orbital Speed (v): {v1.to(u.km/u.s):.2f}\n")


print("--- WORKED EXAMPLE 2: Circular Speed at 400 km ---")
h2 = 400.0 * u.km
r2 = R_E + h2 # 6,778 km

# Circular speed formula: v = sqrt(mu / r)
v2 = np.sqrt(MU_EARTH / r2)

print(f"Orbital Radius (r): {r2:.0f}")
print(f"Circular Speed (v): {v2.to(u.km/u.s):.2f}\n")


print("--- WORKED EXAMPLE 3: Radius of Geostationary Orbit ---")
T3 = 86164.0 * u.s # One sidereal day

# Invert Kepler's 3rd law: a = (mu * T^2 / (4 * pi^2))^(1/3)
a3 = ((MU_EARTH * T3**2) / (4 * np.pi**2)) ** (1 / 3)
h3 = a3 - R_E
v3 = np.sqrt(MU_EARTH / a3)

print(f"Semi-major axis (a): {a3.to(u.km):.0f}")
print(f"GEO Altitude (h): {h3.to(u.km):.0f}")
print(f"Orbital Speed (v): {v3.to(u.km/u.s):.2f}\n")


# =====================================================================
# PART 2: KEPLER SOLVER (NEWTON-RAPHSON)
# =====================================================================
def solve_kepler(M_rad: float, e: float, tol: float = 1e-12) -> float:
    """Solves Kepler's Equation M = E - e*sin(E) using Newton-Raphson method
    and computes the True Anomaly (nu) in degrees.
    """
    # 1. Newton-Raphson iteration for Eccentric Anomaly (E)
    E = M_rad if e < 0.8 else np.pi
    while True:
        f = E - e * np.sin(E) - M_rad
        f_prime = 1.0 - e * np.cos(E)
        delta = f / f_prime
        E -= delta
        if abs(delta) < tol:
            break

    # 2. Convert Eccentric Anomaly (E) to True Anomaly (nu)
    tan_nu_2 = np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2.0)
    nu_rad = 2.0 * np.arctan(tan_nu_2)

    # Convert to degrees and map to [0, 360)
    nu_deg = np.degrees(nu_rad) % 360.0
    return nu_deg


print("--- KEPLER SOLVER VERIFICATION ---")
M_test = 1.0  # radians
e_test = 0.35

nu_calc = solve_kepler(M_test, e_test)
print(f"Inputs:   M = {M_test} rad, e = {e_test}")
print(f"Output:   nu = {nu_calc:.4f} degrees")
print(f"Expected: nu ~ 97.6 degrees")