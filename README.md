# Enterprise Autonomous UAV Fleet Simulation Platform

**Level 3 – Advanced College Project**  
*Coordinated Multi-Agent Autonomous Navigation, Cloud/IoT Telemetry Streaming, Airspace Deconfliction, Predictive Maintenance, and Sustainability Analytics.*

--------------------------------------------------------------------------------

## Overview

The **Enterprise Autonomous UAV Fleet Simulation Platform** is a multi-agent simulation and mission control system. It models concurrent multi-rotor fleet operations across heterogeneous airframes (surveyor quadcopters, heavy-lift logistics hexacopters, and agile patrol scouts), real-time 3D airspace corridor deconfliction, synthetic MQTT/REST edge-to-cloud IoT telemetry, machine learning-ready predictive maintenance, and fleet sustainability analytics.

All mission profiles are loaded dynamically from `fleet_mission_plan.json`, executing synchronized multi-stage survey, logistics, and patrol missions while maintaining strict separation assurance ($d_{\text{min}} > 10.0\text{ m}$) and streaming 10 Hz telemetry into a centralized cloud database.

--------------------------------------------------------------------------------

## Key System Features

- **Heterogeneous Fleet Management**: Concurrently simulates distinct airframe dynamics (mass, rotor count, aerodynamics, thrust-to-weight ratios, and battery configurations).
- **Airspace Separation & Deconfliction**: Implements 3D spatial deconfliction monitoring and altitude corridor stratification ($15\text{ m}, 20\text{ m}, 30\text{ m}$) ensuring zero mid-air conflicts.
- **Edge-to-Cloud IoT Telemetry Broker**: Emulates pub/sub telemetry streaming (`fleet/{id}/telemetry`) with cellular/satcom packet latency jitter ($18 - 42\text{ ms}$) and high ingestion reliability ($99.8\%$).
- **Predictive Maintenance (PdM)**: Analyzes motor bearing vibration spectra ($g_{\text{rms}}$), motor winding thermal dissipation, and battery internal resistance ($R_{\text{int}}$) growth to emit tiered condition-based alerts (`INFO`, `WARNING`, `ALERT`, `CRITICAL`).
- **Sustainability & Carbon Offset Modeling**: Quantifies net carbon emission savings ($kg\text{ CO}_2$) and energy intensity ($Wh/\text{km}$) comparing electric UAV operations against conventional diesel logistics fleets.

--------------------------------------------------------------------------------

## Heterogeneous Fleet Airframe Specifications

| Aircraft ID  | Callsign        | Airframe Type | Primary Enterprise Mission Role                  | Mass (kg) | Rotors | Battery Pack (LiPo) | Operating Alt | Max Speed |
| ------------ | --------------- | ------------- | ------------------------------------------------ | --------- | ------ | ------------------- | ------------- | --------- |
| `UAV-Alpha`  | Surveyor-1      | Quadcopter    | Aerial Photogrammetry & Topographic Mapping      | 1.8 kg    | 4      | 4S 4500 mAh (14.8V) | 20.0 m        | 4.5 m/s   |
| `UAV-Bravo`  | CargoExpress-2  | Hexacopter    | High-Capacity Payload Logistics Transport        | 3.8 kg    | 6      | 6S 8000 mAh (22.2V) | 30.0 m        | 5.5 m/s   |
| `UAV-Charlie`| PatrolScout-3   | Quadcopter    | Perimeter Security & Infrastructure Inspection   | 1.5 kg    | 4      | 4S 4000 mAh (14.8V) | 15.0 m        | 5.0 m/s   |

--------------------------------------------------------------------------------

## Visualizations & Engineering Dashboards

The simulation automatically renders four high-resolution visualizations stored in `results/`:

### 1. 2D Multi-UAV Tracking & Airspace Corridor Map
Displays planned survey corridors against flown trajectories for all three aircraft, including safety separation buffer envelopes ($10.0\text{ m}$) and designated launch pads.
- File: `results/fleet_tracking_2d.png`

### 2. 3D Airspace Deconfliction & Layered Trajectory View
Provides an isometric 3D view illustrating altitude corridor stratification (Layer 1: 20m, Layer 2: 30m, Layer 3: 15m) and vertical ground projections.
- File: `results/fleet_trajectory_3d.png`

### 3. Predictive Maintenance & Vehicle Health Dashboard
A 4-panel diagnostic monitor tracking motor bearing vibration ($g_{\text{rms}}$), winding temperature dynamics, battery internal resistance drift ($m\Omega$), and maintenance alert event counts.
- File: `results/predictive_maintenance_dashboard.png`

### 4. Enterprise Fleet Operations Command Center Dashboard
A 6-panel real-time operational dashboard displaying:
- Coordinated multi-UAV altitude layering
- Fleet ground speed profiles
- Battery State of Charge (SoC) depletion curves
- Pairwise inter-UAV separation distances ($\Delta d_{AB}, \Delta d_{BC}, \Delta d_{AC}$)
- Edge-to-cloud IoT messaging latency distribution
- Sustainability: electric fleet vs. diesel vehicle $\text{CO}_2$ offset comparison
- File: `results/fleet_operations_dashboard.png`

--------------------------------------------------------------------------------

## Fleet Mission Performance & Operational Summary

| Metric Parameter                 | Specification / Limit | Measured Fleet Result | Operational Status                     |
| -------------------------------- | --------------------- | --------------------- | -------------------------------------- |
| Mission Duration (Synchronized)  | < 90.0 s              | 72.4 s                | Completed on Schedule                  |
| Total Fleet Distance Flown       | Multi-sector          | 746.7 m (0.747 km)    | All Waypoint Legs Successfully Cleared |
| Minimum Inter-UAV Separation     | $\ge 10.0\text{ m}$   | 19.51 m               | SECURE – 0 Spatial Conflicts           |
| Airspace Stratification          | Layered               | 15m / 20m / 30m       | 100% Deconfliction Compliance          |
| Total IoT Telemetry Messages     | 10 Hz per UAV         | 2,023 messages        | Continuous Cloud Ingestion             |
| Telemetry Ingestion Reliability  | > 99.0%               | 99.80%                | Enterprise SLA Met                     |
| Mean Cloud Messaging Latency     | < 50.0 ms             | 27.9 ms               | Ultra-Low Latency Pipeline             |
| Total Electrical Energy Used     | Battery Capacity      | 0.0065 kWh (8.7 Wh/km)| High Propulsion Efficiency             |
| Baseline Diesel Van Emissions    | $210\text{ g/km}$     | 0.1568 kg $\text{CO}_2$| Comparative Benchmark                  |
| Net Carbon Emissions Saved       | Offset                | 0.1565 kg $\text{CO}_2$| 99.8% Environmental Footprint Reduction|

--------------------------------------------------------------------------------

## Project Repository Structure

```
uav3/
├── uav_fleet_simulation.py        # Core multi-agent simulation engine & IoT models
├── fleet_mission_plan.json        # Structured multi-UAV mission & airspace plan
├── run_fleet_simulation.sh        # One-click execution shell script
├── README.md                      # Project overview and system features
├── DOCUMENTATION.md               # Technical engineering manual & embedded plots
├── CLOUD_IOT_INTEGRATION.md       # IoT messaging topology & cloud ingestion report
├── FLEET_ANALYTICS_REPORT.md      # Route efficiency, deconfliction & carbon report
├── PREDICTIVE_MAINTENANCE_REPORT.md # Vibration spectra, thermal & battery health report
├── .gitignore                     # Git exclusions (venv/, caches, temporary files)
└── results/
    ├── fleet_tracking_2d.png      # 2D geospatial fleet tracking map
    ├── fleet_trajectory_3d.png    # 3D airspace deconfliction visualization
    ├── predictive_maintenance_dashboard.png # Vehicle health & condition alerts
    ├── fleet_operations_dashboard.png       # 6-panel enterprise command dashboard
    ├── fleet_telemetry.csv        # Comprehensive 10 Hz multi-UAV time-series dataset
    ├── fleet_alerts_log.json      # Machine-readable condition alert event log
    └── fleet_performance_summary.txt # Plain-text executive operations summary
```

--------------------------------------------------------------------------------

## Installation & Execution Guide

### Prerequisites
- macOS, Linux, or Windows
- Python 3.9+
- NumPy & Matplotlib

### Quick Run
Execute the shell script directly in the terminal:
```bash
./run_fleet_simulation.sh
```

### Manual Execution
If running via standard Python:
```bash
# 1. Activate virtual environment (if present)
source venv/bin/activate

# 2. Run the multi-agent fleet simulation
python3 uav_fleet_simulation.py
```

All plots, telemetry CSV datasets, JSON alert logs, and summary text reports are generated automatically inside `results/`.

--------------------------------------------------------------------------------

## Technologies Used

- **Python 3**: Core multi-agent simulation engine and class architecture.
- **NumPy**: Vectorized kinematics, 3D coordinate transformations, and statistical analytics.
- **Matplotlib & mplot3d**: Geospatial 2D path rendering, 3D airspace projections, and enterprise telemetry dashboards.
- **WGS-84 Reference Ellipsoid**: Global geodetic mapping for multi-agent GNSS positions.
- **Simulated MQTT Broker**: Asynchronous IoT pub/sub message architecture with network jitter emulation.
