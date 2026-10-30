# Architecture Revalidation Trade Study: Evaluating Revisit Performance under Realistic Physical Constraints

**Author:** Cao Khanh Tan  
**Project:** Vietnamese Earth Observation Constellation (VEOC)  
**Requirement Focus:** SYS-REQ-01 (Mean Revisit Time < 30.0 minutes)

---

## 1. Executive Summary & Context
Following mentor evaluation, the initial 48-hour geometric coverage model was superseded by a high-fidelity 7-day propagation framework that enforces:
1. Spacecraft Local Vertical Local Horizontal (LVLH) pointing bounds (|roll| <= 30.0°, |pitch| <= 3.0°).
2. Ground elevation mask (>= 10.0°).
3. Optical daylight solar elevation mask (beta_sun >= 10.0°).

Under this physically rigorous model, the Walker Delta 18/3/1 constellation yields:
* **Daytime Mean Revisit Time:** 238.76 minutes (~4.0 hours)
* **7-Day Continuous Optical Mean Revisit:** 1163.74 minutes (~19.4 hours)
* **Worst-Case Revisit Gap (Overnight):** 53.37 hours

Consequently, **SYS-REQ-01 is evaluated as FAIL (Non-Compliant)** under the current pure-optical baseline. This document presents the physical justification for this limitation and explores the trade space of alternative architectures.

---

## 2. Root Causes of Revisit Non-Compliance

### A. The Nocturnal Optical Gap
Optical visible and near-infrared (VNIR) sensors depend on solar irradiance (beta_sun >= 10.0°). Over Vietnam's tropical latitudes (8.5°N - 23.5°N), nighttime lasts 11.5 to 12.5 hours (~700 - 750 minutes) daily. In a pure-optical constellation, no imaging is possible during this nocturnal window. Mathematically, a continuous 24/7 mean revisit time cannot be below 30 minutes because the overnight gap heavily skews the 7-day mean.

### B. SSO Local Time of Ascending Node (LTAN) Geometry
The Walker 18/3/1 architecture distributes 3 planes equally in RAAN (120.0° separation), corresponding to an 8-hour shift in Local Solar Time:
* **Plane 1 (LTAN ~10:30 AM):** Provides ideal daytime mid-morning passes and nighttime passes.
* **Plane 2 (LTAN ~18:30 PM):** Passes during sunset/dusk and sunrise, resulting in low solar elevation angles (< 10.0°).
* **Plane 3 (LTAN ~02:30 AM):** Passes at night and mid-afternoon (~14:30 PM).

Consequently, only 1 to 2 of the 3 planes cross Vietnam during favorable solar elevation windows.

### C. Swath Width vs. Geographic Domain Geometry
In the spacecraft LVLH frame, a roll angle of +/-30.0° yields a cross-track reach of ~292.6 km on either side, providing an instantaneous accessible ground swath of ~585 km.
The territorial extent of Vietnam spans from 102.0°E to 118.0°E, representing a longitude width of ~1712 km at 16°N latitude. An instantaneous 585 km swath covers only ~34% of the target longitude extent in a single pass, preventing simultaneous coverage of inland borders and offshore archipelagos.

---

## 3. Architecture Trade Space Exploration

| Architecture Option | Configuration Details | SYS-REQ-01 Feasibility | Engineering Advantages | System Penalties & Bottlenecks |
| :--- | :--- | :---: | :--- | :--- |
| **Option A: Pure-Optical Fleet Scaling** | Scale to 48 - 72 satellites across 6 - 8 SSO planes clustered between 09:00 and 15:00 LTAN. | **FAIL** (Overnight gaps remain) | Achieves daytime revisit < 30 min during peak sunlight hours. | 3x to 4x cost and launch manifest increase; zero nocturnal capability. |
| **Option B: Enhanced Along-Track Pitch Steering** | Expand pitch agility to +/-30° or +/-45° for look-ahead/look-back imaging. | **FAIL** (Pass frequency unchanged) | Extends pass duration from 30 s to 3-4 min; enables stereo imaging. | Does not increase the number of daily satellite passes; daytime revisit remains ~4.0 hours. |
| **Option C: Low-Inclination Non-SSO Orbit** | Shift inclination to i ~ 20° - 25° at 500 km altitude. | **FAIL** (Nighttime gap remains) | Concentrates all 18 satellites over tropical latitudes, increasing pass frequency by ~3x. | Drifts through local solar times; non-SSO violates SYS-REQ-02; optical imaging remains blind at night. |
| **Option D: Hybrid Optical + SAR Constellation (Recommended)** | Deploy 12 Optical VNIR satellites + 6 Synthetic Aperture Radar (SAR X-band) satellites. | **FEASIBLE (24/7 All-Weather)** | SAR provides active microwave illumination, enabling 24/7 imaging through clouds, rain, and darkness. | Higher bus power demand (SAR duty cycle) and heavier payload mass. |
| **Option E: Requirement Re-baselining** | Retain Walker 18/3/1; redefine SYS-REQ-01 to target daytime mean revisit < 4.0 hours. | **PASS** (Under re-baselined criteria) | Preserves current 18-satellite mass and cost budget; aligns with physical small-sat limits. | Requires formal customer and stakeholder baseline change approval. |

---

## 4. Conclusion & Recommendations
1. **Physical Reality:** Under realistic optical illumination and LVLH pointing constraints, a 18-satellite pure-optical SSO constellation cannot physically achieve a continuous 24/7 mean revisit time of < 30 minutes.
2. **Path Forward:** The optimal path to satisfying rapid all-weather revisit over Vietnam is transitioning to a **Hybrid Optical-SAR constellation** (Option D) or formally re-baselining the optical requirement (Option E) to evaluate daylight operations independently.
