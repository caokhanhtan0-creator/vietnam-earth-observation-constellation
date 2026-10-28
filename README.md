# Vietnam Earth Observation Constellation Design
**Capstone Project - Astrodynamics Specialist Training Program**
*Author:* Cao Khanh Tan  
*Repository Name:* `vietnam-earth-observation-constellation`

---

## 🛰️ Executive Summary & Mission Objective

The **Vietnam Earth Observation Constellation** is a high-performance, cost-optimized low-Earth-orbit (LEO) small satellite constellation designed to provide continuous optical Earth observation over the territory of Vietnam $(8.5^\circ\text{N} - 23.5^\circ\text{N}, 102.0^\circ\text{E} - 118.0^\circ\text{E})$, including mainland, coastal zones, and maritime islands (Paracel & Spratly Islands).

The primary mission objective is to achieve a **mean revisit time of less than 30.0 minutes** across Vietnam for rapid disaster response, agricultural monitoring, maritime security, and environmental surveillance.

---

## 🎯 Problem Statement

Single Earth observation satellites in LEO suffer from long revisit gaps (typically 12 to 24 hours over target latitudes), which are insufficient for time-critical monitoring applications. While a large constellation can reduce revisit gaps, hardware and launch costs scale linearly with satellite count. 

This Capstone project addresses the trade-off between **temporal coverage performance** and **system lifecycle cost** by optimizing a Walker Delta constellation architecture that minimizes satellite count and launch vehicle manifests while strictly satisfying all system engineering requirements.

---

## 📋 System Requirements (Requirements Baseline)

The mission design is governed by six verifiable system requirements (`SYS-REQ-01` to `SYS-REQ-06`):

| Requirement ID | Description | Threshold Value | Verification Method |
| :--- | :--- | :---: | :---: |
| **SYS-REQ-01** | Mean revisit time across Vietnam territory $(8.5^\circ\text{N} - 23.5^\circ\text{N})$ | $< 30.0\text{ min}$ | Numerical Simulation |
| **SYS-REQ-02** | Maintain operational altitude within deadband over 5-year lifetime | $500.0\text{ km} \pm 5.0\text{ km}$ | Analytical & Simulation |
| **SYS-REQ-03** | Onboard propulsion total \\(\Delta v\\) capability | $\ge 300.0\text{ m/s}$ | Budget Analysis |
| **SYS-REQ-04** | End-of-Life (EOL) deorbit re-entry duration | $< 2.0\text{ years}$ | Orbital Decay Analysis |
| **SYS-REQ-05** | Payload optical cross-track roll-steering capability | $\ge \pm 30.0^\circ$ | Inspection & Simulation |
| **SYS-REQ-06** | Maximum wet mass per satellite | $\le 150.0\text{ kg}$ | Mass Budget Analysis |

---

## 📐 Selected Architecture: Walker Delta $97.4^\circ : 18 / 3 / 1$

Through an exhaustive trade study comparing 79 candidate constellation topologies, the **Walker Delta $97.4^\circ : 18 / 3 / 1$** configuration was selected as the optimal Full Operational Capability (FOC) architecture.

### Key Technical Baseline Specifications
* **Total Satellites ($N$)**: **18 small satellites**
* **Orbital Planes ($P$)**: **3 planes** (6 satellites per plane)
* **Inter-Plane Phasing ($F$)**: **1**
* **Operational Altitude ($h$)**: **500.0 km** (Sun-Synchronous Orbit - SSO)
* **Inclination $(i)$**: **97.402°**
* **Payload Steering**: **$\pm 30.0^\circ$ Cross-Track Roll Steering** (LVLH body-frame pointing)
* **Propulsion Capability**: **300.0 m/s total onboard $\Delta v$**
* **Lifetime $\Delta v$ Requirement**: **252.0 m/s** (includes 20% margin)
* **Mass Allocation**: **150.0 kg wet mass / satellite** (900 kg wet mass per orbital plane)

---

## 💻 Tools & Technologies Used

* **Language**: Python 3.11+
* **Numerical Libraries**: `NumPy` (high-performance vector operations), `Pandas` (data aggregation)
* **Astrodynamics Libraries**: Custom WGS-84 \\(J_2\\) orbit propagator, `Skyfield` / `SGP4` (verification)
* **Visualization**: `Matplotlib`, `Seaborn`
* **Documentation**: LaTeX, Pandoc, `python-docx`

---

## 🔬 Simulation Methodology

The numerical simulation framework models 48 hours of continuous orbit propagation $5,761$ time steps at $\Delta t = 30.0\text{ s}$ using a WGS-84 $J_2$ spherical harmonic perturbation model:

1. **Orbit Propagation**: Integrates $J_2$ nodal regression rate $(\dot{\Omega} = +0.9856^\circ/\text{day})$ and Earth mean motion ($n = 1.1068 \times 10^{-3}\text{ rad/s})$.
2. **Coordinate Transformations**: Transforms satellite positions from Orbital Frame $ECI \to ECEF$ considering Earth rotation $(\omega_E = 7.292115 \times 10^{-5}\text{ rad/s})$.
3. **Target Grid**: Evaluates access over a geographical grid of **132 target nodes** covering Vietnam $(1.5^\circ \times 1.5^\circ)$ grid spacing) plus 5 strategic locations (Hanoi, Da Nang, Ho Chi Minh City, Paracel Islands, Spratly Islands).
4. **Pointing Geometry**: Implements dynamic LVLH cross-track roll steering bounds $|\theta_{\text{roll}}| \le 30.0^\circ$, $|\theta_{\text{pitch}}| \le 3.0^\circ$.

---

## 📊 Main Results & Requirements Verification

### 1. Revisit Time & Coverage Performance (48-Hour Simulation)

| Target Location | Coordinates | Passes (48h) | Fixed Nadir Revisit | **Active Steer Revisit (\\(\pm 30^\circ\\))** | Mean Access | Coverage % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hanoi (Capital)** | $21.03^\circ\text{N}, 105.85^\circ\text{E}$ | 63 | $39.40\text{ min}$ | **$20.49\text{ min}$** | $5.67\text{ min}$ | $12.41\%$ |
| **Da Nang (Central)** | $16.05^\circ\text{N}, 108.20^\circ\text{E}$ | 60 | $43.16\text{ min}$ | **$22.44\text{ min}$** | $5.78\text{ min}$ | $12.03\%$ |
| **Ho Chi Minh City** | $10.82^\circ\text{N}, 106.63^\circ\text{E}$ | 59 | $44.03\text{ min}$ | **$22.89\text{ min}$** | $5.76\text{ min}$ | $11.80\%$ |
| **Paracel Is. (Hoang Sa)** | $16.50^\circ\text{N}, 112.00^\circ\text{E}$ | 61 | $42.74\text{ min}$ | **$22.23\text{ min}$** | $5.67\text{ min}$ | $12.01\%$ |
| **Spratly Is. (Truong Sa)**| $8.65^\circ\text{N}, 111.92^\circ\text{E}$ | 59 | $44.10\text{ min}$ | **$22.93\text{ min}$** | $5.70\text{ min}$ | $11.68\%$ |
| **VIETNAM GRID AVG (132)** | **Nationwide** | **61.0** | **$42.01\text{ min}$** | **$25.70\text{ min}$** | **$5.69\text{ min}$** | **$18.17\%$** |

*Cross-Verification Note:* The simulated active-steering mean revisit time of **$25.70\text{ min}$** agrees remarkably well with the analytical prediction of **$25.56\text{ min}$** $(+0.55\%$ deviation).

### 2. Master Requirements Verification Matrix

**All six system requirements pass with non-negative engineering margins:**

| Req ID | Parameter / Subject | Threshold | Achieved Value | Margin | Status |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **SYS-REQ-01** | Mean Revisit Time | $< 30.0\text{ min}$ | **$25.70\text{ min}$** | $+14.33\%$ | **PASS** |
| **SYS-REQ-02** | 5-Year Altitude Deadband | $500\text{ km} \pm 5\text{ km}$ | **$500.0\text{ km} \pm 5.0\text{ km}$** | $0.0\%$ | **PASS** |
| **SYS-REQ-03** | Onboard Propulsion $\Delta v$ | $\ge 300.0\text{ m/s}$ | **$300.0\text{ m/s}$ capability** | $+19.05\%$ | **PASS** |
| **SYS-REQ-04** | EOL Re-entry Duration | $< 2.0\text{ years}$ | **$15 - 45\text{ days}$** ($h_p = 150\text{ km}$) | $+93.8\%$ | **PASS** |
| **SYS-REQ-05** | Cross-Track Roll Steering | $\ge \pm 30.0^\circ$ | **$\pm 30.0^\circ$ Cross-Track** | $0.0\%$ | **PASS** |
| **SYS-REQ-06** | Satellite Wet Mass | $\le 150.0\text{ kg}$ | **$150.0\text{ kg}$ / satellite** | $0.0\%$ | **PASS** |

---

## ⚡ Lifetime $\Delta v$ Budget Summary

The total lifetime propulsion requirement is **$252.0\text{ m/s}$** (including a 20% margin):

$\Delta v_{\text{total}} = \Delta v_{\text{LEOP}} + \Delta v_{\text{drag}} + \Delta v_{\text{CAM}} + \Delta v_{\text{deorbit}} = 72.0 + 50.0 + 20.0 + 110.0 = 252.0\text{ m/s}$

* **LEOP / Phase Adjustment**: $72.0\text{ m/s}$ (Phasing maneuvers post-rideshare separation).
* **5-Year Drag Makeup**: $50.0\text{ m/s}$ (Maintains $\pm 5\text{ km}$ deadband under atmospheric drag decay of $\sim 4.4\text{ km/yr}$).
* **Collision Avoidance (CAM)**: $20.0\text{ m/s}$ (Emergency conjunction avoidance).
* **EOL De-orbit Burn**: $110.0\text{ m/s}$ (Lowers perigee from $500\text{ km}$ to $150\text{ km}$ for rapid atmospheric destruction in $< 45\text{ days}$).
* **Propulsion System Capability**: $300.0\text{ m/s}$ provided $\to$ **$+19.05\%$ positive margin**.

---

## 🚀 Quickstart: Running the Python Simulation

### Prerequisites
* Python 3.10+
* `numpy`, `pandas`

### Installation & Execution
```bash
# Clone the repository
git clone https://github.com/your-username/vietnam-earth-observation-constellation.git
cd vietnam-earth-observation-constellation

# Install dependencies
pip install -r requirements.txt

# Run the 48-hour orbit propagation simulation
python3.11 src/session12.py
```

## 🛠️ Key Assumptions & Limitations
1. **48-Hour Simulation Horizon:** The 48-hour window provides a statistically representative sample for revisit gap analysis under $J_2$ precession, but full solar cycle variations ($F_{10.7}$) were modeled analytically.
2. **Payload Steering Kinematics:** Attitude maneuver settling times (ADCS slew rates) were assumed instantaneous within the $\pm 30.0^\circ$ cross-track roll limits; full multi-body attitude dynamics will be validated in Phase B.
3. **Atmospheric Drag Model:** A static exponential density model was used for $500\text{ km}$ LEO decay calculations. High-fidelity NRLMSISE-00 atmospheric modeling is recommended for detailed flight software implementation.

## 🎓 Lessons Learned & Future Improvements
* **Trade Space Reduction:** Transitioning from the $24/4/1$ baseline to the optimized $18/3/1$ architecture reduced satellite hardware costs by 25% and saved 1 full launch vehicle manifest while fully meeting the $< 30\text{ min}$ revisit requirement.
* **Future Phase B Work:** 
   * Integration of ground station contact schedules (Hanoi, Da Nang, Ho Chi Minh City ground stations).
   * Modeling inter-satellite links (ISL) for real-time data relay.
   * Fine-grained ADCS actuator sizing for $\pm 30^\circ$ roll maneuvers.
## 📁 Repository Directory Structure
```text
vietnam-earth-observation-constellation/
├── README.md                 # Project overview and instructions
├── requirements.txt          # Python dependency packages (NumPy, Pandas, etc.)
├── src/                      # Simulation source code
│   ├── session1.py ~ s10.py  # Calculation and verification modules
│   └── session12.py          # Main script for 48-hour orbit propagation simulation
├── results/                  # Simulation output data (132-grid & strategic targets)
├── figures/                  # Orbit plots, J2 perturbation graphs, and coverage maps
├── docs/                     # Astrodynamics theory and reference documents
├── report/                   # Comprehensive technical reports (PDF)
├── slides/                   # System architecture presentation slides
└── defense/                  # Capstone defense question bank and preparation files