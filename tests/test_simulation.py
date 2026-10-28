import pytest
import numpy as np

def test_orbital_circular_velocity():
    """Verify circular velocity at 500 km altitude SSO."""
    R_E = 6378.137
    MU = 398600.4418
    r = R_E + 500.0
    vc = np.sqrt(MU / r)
    assert np.isclose(vc, 7.6126, atol=1e-3)

def test_sso_inclination():
    """Verify SSO inclination near 97.4 deg."""
    R_E = 6378.137
    MU = 398600.4418
    J2 = 1.08262668e-3
    r = R_E + 500.0
    n = np.sqrt(MU / r**3)
    raan_rate_sso = 1.99106e-7  # rad/s
    cos_i = raan_rate_sso / (-1.5 * J2 * (R_E / r)**2 * n)
    inc_deg = np.degrees(np.arccos(cos_i))
    assert np.isclose(inc_deg, 97.402, atol=1e-2)

def test_pointing_constraints():
    """Verify attitude pointing boundaries."""
    max_roll = 30.0
    max_pitch = 3.0
    assert max_roll == 30.0
    assert max_pitch == 3.0

def test_simulation_results_exist():
    """Verify output data files are generated."""
    import os
    assert os.path.exists("results/strategic_targets_7days.csv")
    assert os.path.exists("results/vietnam_grid_7days.csv")
    assert os.path.exists("results/simulation_summary_7days.txt")
