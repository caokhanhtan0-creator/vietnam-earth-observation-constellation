import pytest
import numpy as np

R_E = 6378.137
ALTITUDE = 500.0
r = R_E + ALTITUDE
MU = 398600.4418
vc = np.sqrt(MU / r)

def test_orbital_circular_velocity():
    """Verify circular velocity at 500 km altitude SSO."""
    assert np.isclose(vc, 7.6126, atol=1e-3)

def test_lvlh_frame_orthonormality():
    """Verify that the spacecraft LVLH basis vectors are mutually orthogonal and unit-length."""
    r_sat = np.array([r, 0.0, 0.0])
    v_sat = np.array([0.0, vc, 0.0])
    
    z_lvlh = -r_sat / np.linalg.norm(r_sat)
    h_vec = np.cross(r_sat, v_sat)
    y_lvlh = -h_vec / np.linalg.norm(h_vec)
    x_lvlh = np.cross(y_lvlh, z_lvlh)
    
    assert np.isclose(np.linalg.norm(x_lvlh), 1.0)
    assert np.isclose(np.linalg.norm(y_lvlh), 1.0)
    assert np.isclose(np.linalg.norm(z_lvlh), 1.0)
    assert np.isclose(np.dot(x_lvlh, y_lvlh), 0.0, atol=1e-7)
    assert np.isclose(np.dot(y_lvlh, z_lvlh), 0.0, atol=1e-7)
    assert np.isclose(np.dot(x_lvlh, z_lvlh), 0.0, atol=1e-7)

def test_lvlh_target_pointing_angles():
    """Verify roll and pitch angle extraction for a nadir and an off-nadir target."""
    r_sat = np.array([r, 0.0, 0.0])
    v_sat = np.array([0.0, vc, 0.0])
    z_lvlh = -r_sat / np.linalg.norm(r_sat)
    h_vec = np.cross(r_sat, v_sat)
    y_lvlh = -h_vec / np.linalg.norm(h_vec)
    x_lvlh = np.cross(y_lvlh, z_lvlh)
    
    # Target 1: Pure Nadir ground target
    r_tgt_nadir = np.array([R_E, 0.0, 0.0])
    los_nadir = r_tgt_nadir - r_sat
    rho_x = np.dot(los_nadir, x_lvlh)
    rho_y = np.dot(los_nadir, y_lvlh)
    rho_z = np.dot(los_nadir, z_lvlh)
    roll_nadir = np.degrees(np.arctan2(rho_y, rho_z))
    pitch_nadir = np.degrees(np.arctan2(rho_x, rho_z))
    
    assert np.isclose(roll_nadir, 0.0, atol=1e-5)
    assert np.isclose(pitch_nadir, 0.0, atol=1e-5)
    assert rho_z > 0.0  # Must be below local horizon
    
    # Target 2: Target offset cross-track by exactly 25.0 degrees roll
    target_roll_expected = 25.0
    los_offset = 500.0 * np.tan(np.radians(target_roll_expected)) * y_lvlh + 500.0 * z_lvlh
    roll_calc = np.degrees(np.arctan2(np.dot(los_offset, y_lvlh), np.dot(los_offset, z_lvlh)))
    pitch_calc = np.degrees(np.arctan2(np.dot(los_offset, x_lvlh), np.dot(los_offset, z_lvlh)))
    
    assert np.isclose(roll_calc, target_roll_expected, atol=1e-5)
    assert np.isclose(pitch_calc, 0.0, atol=1e-5)

def test_solar_elevation_daylight_filter():
    """Verify that solar elevation distinguishes between midday illumination and nighttime."""
    target_normal = np.array([1.0, 0.0, 0.0])
    
    # Noon Sun (subsolar point directly overhead target)
    sun_noon = np.array([1.0, 0.0, 0.0])
    cos_sza_noon = np.dot(target_normal, sun_noon)
    solar_elev_noon = 90.0 - np.degrees(np.arccos(np.clip(cos_sza_noon, -1.0, 1.0)))
    assert np.isclose(solar_elev_noon, 90.0)
    assert solar_elev_noon >= 10.0  # Authorized for optical imaging
    
    # Night Sun (opposite side of Earth)
    sun_night = np.array([-1.0, 0.0, 0.0])
    cos_sza_night = np.dot(target_normal, sun_night)
    solar_elev_night = 90.0 - np.degrees(np.arccos(np.clip(cos_sza_night, -1.0, 1.0)))
    assert np.isclose(solar_elev_night, -90.0)
    assert solar_elev_night < 10.0  # Rejected by optical daylight condition