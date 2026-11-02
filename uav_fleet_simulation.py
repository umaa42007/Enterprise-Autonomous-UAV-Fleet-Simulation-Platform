#!/usr/bin/env python3
"""
Enterprise Autonomous UAV Fleet Simulation Platform (Level 3 - Advanced)
Multi-agent 3D guidance, IoT cloud telemetry, predictive maintenance, and sustainability analytics.
"""

import os
# Configure Matplotlib cache directory inside scratch/tmp to avoid permission warnings
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"

import json
import math
import random
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Fixed seed for deterministic, reproducible simulation
random.seed(42)
np.random.seed(42)

# ==============================================================================
# 1. PHYSICAL & GEODETIC CONSTANTS
# ==============================================================================
GRAVITY = 9.80665              # m/s^2
AIR_DENSITY = 1.225            # kg/m^3 (sea level standard)
DIESEL_EMISSION_G_PER_KM = 210.0 # g CO2/km (standard light delivery van)
GRID_EMISSION_KG_PER_KWH = 0.042 # kg CO2/kWh (renewable/clean grid standard)


# ==============================================================================
# 2. WGS-84 GEODETIC CONVERTER
# ==============================================================================
class WGS84Converter:
    """Transforms local Cartesian North-East-Down (NED) coordinates to geodetic WGS-84."""
    A = 6378137.0
    F = 1.0 / 298.257223563
    B = A * (1.0 - F)
    E_SQ = 2.0 * F - F * F

    def __init__(self, ref_lat_deg: float, ref_lon_deg: float, ref_alt_m: float):
        self.ref_lat = math.radians(ref_lat_deg)
        self.ref_lon = math.radians(ref_lon_deg)
        self.ref_alt = ref_alt_m
        sin_lat = math.sin(self.ref_lat)
        self.rn = self.A / math.sqrt(1.0 - self.E_SQ * sin_lat * sin_lat)
        self.rm = (self.A * (1.0 - self.E_SQ)) / ((1.0 - self.E_SQ * sin_lat * sin_lat) ** 1.5)

    def ned_to_geodetic(self, east_m: float, north_m: float, alt_m: float):
        d_lat = (north_m / (self.rm + self.ref_alt))
        d_lon = (east_m / ((self.rn + self.ref_alt) * math.cos(self.ref_lat)))
        lat_deg = math.degrees(self.ref_lat + d_lat)
        lon_deg = math.degrees(self.ref_lon + d_lon)
        height_m = self.ref_alt + alt_m
        return lat_deg, lon_deg, height_m


# ==============================================================================
# 3. IOT CLOUD TELEMETRY & MESSAGE BROKER
# ==============================================================================
class CloudIoTBroker:
    """Simulates an enterprise MQTT/REST IoT telemetry broker with latency and packet health."""
    def __init__(self):
        self.published_messages = 0
        self.delivered_messages = 0
        self.dropped_messages = 0
        self.latencies_ms = []
        self.alerts = []

    def publish_telemetry(self, drone_id: str, payload: dict) -> dict:
        self.published_messages += 1
        # Realistic IoT cellular/satcom latency jitter: 18 - 42 ms
        latency = random.gauss(28.0, 4.5)
        latency = max(15.0, min(55.0, latency))
        self.latencies_ms.append(latency)

        # 99.9% packet delivery rate
        if random.random() < 0.001:
            self.dropped_messages += 1
            return {"status": "DROPPED", "latency_ms": latency}

        self.delivered_messages += 1
        return {"status": "DELIVERED", "latency_ms": latency, "payload": payload}

    def emit_alert(self, drone_id: str, timestamp_s: float, severity: str, metric: str, value: float, message: str):
        alert_event = {
            "timestamp_s": round(timestamp_s, 2),
            "drone_id": drone_id,
            "severity": severity,
            "metric": metric,
            "value": round(value, 3),
            "message": message
        }
        self.alerts.append(alert_event)


# ==============================================================================
# 4. PREDICTIVE MAINTENANCE & VEHICLE HEALTH MODEL
# ==============================================================================
class PredictiveMaintenanceModel:
    """Simulates vibration harmonics, motor thermal heat-up, and battery health degradation."""
    def __init__(self, drone_id: str, has_simulated_fault: bool = False):
        self.drone_id = drone_id
        self.has_fault = has_simulated_fault
        self.vibration_g = 0.18        # Nominal RMS vibration (g)
        self.motor_temp_c = 28.0       # Ambient baseline (°C)
        self.soh_pct = 99.8            # State of Health (%)
        self.internal_resistance_ohm = 0.018 # Initial internal resistance (Ohms)
        self.total_stress_accum = 0.0

    def update(self, dt: float, current_speed: float, thrust_n: float, time_s: float, broker: CloudIoTBroker):
        # 1. Motor Bearing Vibration
        # Nominal baseline vibration scales with thrust and speed
        base_vib = 0.16 + 0.003 * thrust_n + 0.004 * current_speed + random.gauss(0, 0.015)

        # UAV-Bravo develops an anomalous high-vibration signature during transit at t > 35s
        if self.has_fault and time_s > 35.0:
            fault_growth = min(0.68, (time_s - 35.0) * 0.022)
            self.vibration_g = base_vib + fault_growth + random.gauss(0, 0.025)
        else:
            self.vibration_g = max(0.12, base_vib)

        # 2. Motor Winding Thermal Model
        # Electrical resistive heating balanced by active aerodynamic cooling
        heat_input = 0.048 * (thrust_n ** 0.82)
        cooling = 0.075 * (self.motor_temp_c - 28.0) * (1.0 + 0.12 * current_speed)
        self.motor_temp_c = max(28.0, min(75.0, self.motor_temp_c + dt * (heat_input - cooling)))

        # 3. Battery Degradation & Internal Resistance Growth
        self.total_stress_accum += dt * thrust_n
        self.soh_pct = max(94.0, 99.8 - (self.total_stress_accum * 0.00035))
        self.internal_resistance_ohm = 0.018 + (100.0 - self.soh_pct) * 0.0012

        # 4. Automated Condition Alerts
        if self.vibration_g > 0.85 and time_s > 36.0 and int(time_s * 10) % 150 == 0:
            broker.emit_alert(
                self.drone_id, time_s, "WARNING", "motor_vibration_g",
                self.vibration_g, "Elevated bearing vibration detected (> 0.85g). Scheduled inspection recommended."
            )
        if self.motor_temp_c > 52.0 and int(time_s * 10) % 200 == 0:
            broker.emit_alert(
                self.drone_id, time_s, "ALERT", "motor_temp_c",
                self.motor_temp_c, "Motor winding temperature exceeded threshold (> 52°C)."
            )


# ==============================================================================
# 5. INDIVIDUAL UAV AGENT CLASS
# ==============================================================================
class UAVAgent:
    """Encapsulates kinematics, guidance, battery, and state for one autonomous drone."""
    def __init__(self, config: dict, geo_converter: WGS84Converter, has_fault: bool = False):
        self.id = config["drone_id"]
        self.callsign = config["callsign"]
        self.airframe = config["airframe_type"]
        self.role = config["role"]
        self.mass = config["mass_kg"]
        self.rotor_count = config["rotor_count"]
        self.battery_cap_mah = config["battery_capacity_mah"]
        self.nominal_voltage = config["nominal_voltage_v"]
        self.cruising_speed = config["cruising_speed_mps"]
        self.target_alt = config["target_altitude_m"]
        self.waypoints = config["waypoints"]

        # Initial launch positions
        offset = config.get("launch_offset", {"x_m": 0.0, "y_m": 0.0, "z_m": 0.0})
        self.x = offset["x_m"]
        self.y = offset["y_m"]
        self.z = offset["z_m"]
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.current_wp_idx = 0
        self.completed = False

        # Battery & Power
        self.soc_pct = 100.0
        self.voltage = self.nominal_voltage * 1.135
        self.total_energy_wh = 0.0
        self.current_draw_a = 0.0
        self.total_distance_flown = 0.0
        self.cross_track_error = 0.0
        self.history = []

        # Subsystems
        self.geo = geo_converter
        self.pdm = PredictiveMaintenanceModel(self.id, has_simulated_fault=has_fault)

    def compute_cross_track_error(self) -> float:
        """Calculates orthogonal distance from UAV position to nominal active waypoint leg."""
        if self.current_wp_idx == 0:
            wp_curr = self.waypoints[0]
            dx = self.x - wp_curr["x_m"]
            dy = self.y - wp_curr["y_m"]
            return math.sqrt(dx * dx + dy * dy)

        wp_prev = self.waypoints[self.current_wp_idx - 1]
        wp_curr = self.waypoints[self.current_wp_idx]

        leg_x = wp_curr["x_m"] - wp_prev["x_m"]
        leg_y = wp_curr["y_m"] - wp_prev["y_m"]
        leg_len = math.sqrt(leg_x * leg_x + leg_y * leg_y)

        if leg_len < 1e-4:
            return 0.0

        u_x = leg_x / leg_len
        u_y = leg_y / leg_len
        rel_x = self.x - wp_prev["x_m"]
        rel_y = self.y - wp_prev["y_m"]

        # Signed 2D cross product: u_x * rel_y - u_y * rel_x
        return u_x * rel_y - u_y * rel_x

    def step(self, dt: float, time_s: float, broker: CloudIoTBroker):
        if self.completed:
            return

        target_wp = self.waypoints[self.current_wp_idx]
        tx = target_wp["x_m"]
        ty = target_wp["y_m"]
        tz = target_wp["z_m"]
        target_speed = target_wp["speed_mps"]

        # 1. Waypoint Guidance & Line-of-Sight Law
        dx = tx - self.x
        dy = ty - self.y
        dz = tz - self.z
        dist_2d = math.sqrt(dx * dx + dy * dy)
        dist_3d = math.sqrt(dx * dx + dy * dy + dz * dz)

        # Waypoint Acceptance Check (radius = 2.5m)
        if dist_3d < 2.5:
            if self.current_wp_idx < len(self.waypoints) - 1:
                self.current_wp_idx += 1
                target_wp = self.waypoints[self.current_wp_idx]
                tx = target_wp["x_m"]
                ty = target_wp["y_m"]
                tz = target_wp["z_m"]
                target_speed = target_wp["speed_mps"]
                dx = tx - self.x
                dy = ty - self.y
                dz = tz - self.z
                dist_2d = math.sqrt(dx * dx + dy * dy)
            else:
                if self.z <= 0.2:
                    self.completed = True
                    self.vx = self.vy = self.vz = 0.0

        # Calculate desired heading
        path_heading = math.atan2(dy, dx)
        self.cross_track_error = self.compute_cross_track_error()

        # LOS heading adjustment based on cross-track correction
        lookahead = 6.0
        cte_correction = math.atan2(-0.85 * self.cross_track_error, lookahead)
        desired_yaw = path_heading + cte_correction

        # Steering dynamics
        yaw_err = math.atan2(math.sin(desired_yaw - self.yaw), math.cos(desired_yaw - self.yaw))
        self.yaw += 1.8 * yaw_err * dt

        # Velocity tracking
        desired_vxy = min(target_speed, max(0.5, dist_2d * 0.8)) if dist_2d > 0.5 else 0.0
        target_vx = desired_vxy * math.cos(self.yaw)
        target_vy = desired_vxy * math.sin(self.yaw)

        # Vertical velocity control
        target_vz = max(-2.0, min(2.5, dz * 0.9))

        # First-order motor/inertial lag
        tau = 0.12
        self.vx += (target_vx - self.vx) * (dt / tau)
        self.vy += (target_vy - self.vy) * (dt / tau)
        self.vz += (target_vz - self.vz) * (dt / tau)

        # Update position
        disp_x = self.vx * dt
        disp_y = self.vy * dt
        disp_z = self.vz * dt
        self.x += disp_x
        self.y += disp_y
        self.z = max(0.0, self.z + disp_z)

        step_dist = math.sqrt(disp_x * disp_x + disp_y * disp_y + disp_z * disp_z)
        self.total_distance_flown += step_dist

        # Attitude angles (banking during turns and acceleration)
        self.pitch = math.degrees(math.atan2(-self.vx * math.cos(self.yaw) - self.vy * math.sin(self.yaw), GRAVITY))
        self.roll = math.degrees(math.atan2(self.vx * math.sin(self.yaw) - self.vy * math.cos(self.yaw), GRAVITY))

        # 2. Propulsion & Battery Model
        hover_thrust = self.mass * GRAVITY
        drag_force = 0.5 * AIR_DENSITY * 0.35 * 0.08 * (self.vx * self.vx + self.vy * self.vy)
        total_thrust = hover_thrust + drag_force + (self.mass * abs(self.vz))

        # Power calculation
        induced_power = (total_thrust ** 1.5) / math.sqrt(2.0 * AIR_DENSITY * 0.25 * self.rotor_count)
        electrical_power = (induced_power / 0.78) + 15.0  # Avionics overhead
        self.current_draw_a = electrical_power / self.voltage

        # Coulomb integration
        discharged_mah = (self.current_draw_a * (dt / 3600.0)) * 1000.0
        used_soc_delta = (discharged_mah / self.battery_cap_mah) * 100.0
        self.soc_pct = max(0.0, self.soc_pct - used_soc_delta)
        self.total_energy_wh += (electrical_power * (dt / 3600.0))
        self.voltage = self.nominal_voltage * (0.92 + 0.20 * (self.soc_pct / 100.0))

        # 3. Predictive Maintenance Update
        ground_speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        self.pdm.update(dt, ground_speed, total_thrust, time_s, broker)

        # 4. Geodetic Coordinates
        lat, lon, msl_alt = self.geo.ned_to_geodetic(self.x, self.y, self.z)

        # 5. Cloud IoT Telemetry Publishing
        telemetry_payload = {
            "timestamp_s": round(time_s, 2),
            "drone_id": self.id,
            "callsign": self.callsign,
            "x_m": round(self.x, 2),
            "y_m": round(self.y, 2),
            "z_m": round(self.z, 2),
            "lat_deg": round(lat, 6),
            "lon_deg": round(lon, 6),
            "speed_mps": round(ground_speed, 2),
            "heading_deg": round(math.degrees(self.yaw) % 360, 1),
            "cross_track_error_m": round(self.cross_track_error, 3),
            "soc_pct": round(self.soc_pct, 1),
            "battery_v": round(self.voltage, 2),
            "vibration_g": round(self.pdm.vibration_g, 3),
            "motor_temp_c": round(self.pdm.motor_temp_c, 1),
            "battery_soh_pct": round(self.pdm.soh_pct, 2),
            "internal_res_ohm": round(self.pdm.internal_resistance_ohm, 4),
            "active_wp": self.current_wp_idx
        }
        broker.publish_telemetry(self.id, telemetry_payload)

        # Record history
        self.history.append(telemetry_payload)


# ==============================================================================
# 6. ENTERPRISE FLEET SIMULATION MANAGER
# ==============================================================================
class FleetSimulationManager:
    """Coordinates multiple UAVs, deconfliction, metrics, and visualization."""
    def __init__(self, mission_file_path: str):
        with open(mission_file_path, "r") as f:
            self.config = json.load(f)

        base = self.config["base_station"]
        self.geo = WGS84Converter(base["reference_latitude_deg"], base["reference_longitude_deg"], base["elevation_msl_m"])
        self.broker = CloudIoTBroker()

        # Instantiate heterogeneous fleet
        self.fleet = [
            UAVAgent(self.config["fleet"][0], self.geo, has_fault=False), # Alpha: Photogrammetry
            UAVAgent(self.config["fleet"][1], self.geo, has_fault=True),  # Bravo: Heavy Cargo with simulated bearing wear
            UAVAgent(self.config["fleet"][2], self.geo, has_fault=False)  # Charlie: Agile Security Scout
        ]

        self.min_separation_recorded = float("inf")
        self.separation_violations = 0
        self.separation_history = []
        self.time_history = []

    def run(self, dt: float = 0.1, max_duration_s: float = 85.0):
        print("=================================================================")
        print(" STARTING ENTERPRISE AUTONOMOUS UAV FLEET SIMULATION (LEVEL 3)")
        print(f" Fleet Size: {len(self.fleet)} Autonomous Airframes")
        print("=================================================================")

        time_s = 0.0
        while time_s <= max_duration_s:
            all_done = True
            for drone in self.fleet:
                drone.step(dt, time_s, self.broker)
                if not drone.completed:
                    all_done = False

            # Check Airspace Deconfliction between all pairs
            d_ab = math.sqrt((self.fleet[0].x - self.fleet[1].x)**2 + (self.fleet[0].y - self.fleet[1].y)**2 + (self.fleet[0].z - self.fleet[1].z)**2)
            d_bc = math.sqrt((self.fleet[1].x - self.fleet[2].x)**2 + (self.fleet[1].y - self.fleet[2].y)**2 + (self.fleet[1].z - self.fleet[2].z)**2)
            d_ac = math.sqrt((self.fleet[0].x - self.fleet[2].x)**2 + (self.fleet[0].y - self.fleet[2].y)**2 + (self.fleet[0].z - self.fleet[2].z)**2)

            min_dist = min(d_ab, d_bc, d_ac)
            if min_dist < self.min_separation_recorded and time_s > 5.0: # Skip ground launch pad phase
                self.min_separation_recorded = min_dist

            if min_dist < 10.0 and time_s > 5.0:
                self.separation_violations += 1

            self.separation_history.append((d_ab, d_bc, d_ac))
            self.time_history.append(time_s)

            if all_done:
                print(f"[INFO] All fleet airframes landed and disarmed at t = {time_s:.1f}s.")
                break

            time_s += dt

        print("=================================================================")
        print(f" FLEET MISSION COMPLETE in {time_s:.1f}s")
        print(f" Minimum Inter-Vehicle Separation: {self.min_separation_recorded:.2f} m (Safe: > 10.0 m)")
        print(f" Total IoT Cloud Messages Processed: {self.broker.delivered_messages}")
        print("=================================================================")

    def export_telemetry_csv(self, output_path: str):
        headers = [
            "timestamp_s", "drone_id", "callsign", "x_m", "y_m", "z_m",
            "lat_deg", "lon_deg", "speed_mps", "heading_deg", "cross_track_error_m",
            "soc_pct", "battery_v", "vibration_g", "motor_temp_c", "battery_soh_pct",
            "internal_res_ohm", "active_wp"
        ]
        # Interleave records chronologically
        all_records = []
        for drone in self.fleet:
            all_records.extend(drone.history)
        all_records.sort(key=lambda r: (r["timestamp_s"], r["drone_id"]))

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in all_records:
                writer.writerow(r)

        print(f"Exported {len(all_records)} multi-UAV telemetry rows to: {output_path}")

    def export_alerts_json(self, output_path: str):
        with open(output_path, "w") as f:
            json.dump(self.broker.alerts, f, indent=2)
        print(f"Exported {len(self.broker.alerts)} alert events to: {output_path}")

    def export_summary_report(self, output_path: str):
        # Calculate sustainability metrics
        total_flown_km = sum(d.total_distance_flown for d in self.fleet) / 1000.0
        total_energy_kwh = sum(d.total_energy_wh for d in self.fleet) / 1000.0
        electric_fleet_co2_kg = total_energy_kwh * GRID_EMISSION_KG_PER_KWH
        equivalent_diesel_co2_kg = total_flown_km * (DIESEL_EMISSION_G_PER_KM / 1000.0)
        co2_saved_kg = max(0.0, equivalent_diesel_co2_kg - electric_fleet_co2_kg)
        carbon_reduction_pct = (co2_saved_kg / equivalent_diesel_co2_kg * 100.0) if equivalent_diesel_co2_kg > 0 else 0.0

        with open(output_path, "w") as f:
            f.write("================================================================================\n")
            f.write("LEVEL 3 - ADVANCED: ENTERPRISE AUTONOMOUS UAV FLEET PLATFORM\n")
            f.write("================================================================================\n")
            f.write("Executive Fleet Operations, Safety & Sustainability Report\n\n")

            f.write("1. FLEET PERFORMANCE METRICS\n")
            f.write("--------------------------------------------------------------------------------\n")
            for d in self.fleet:
                f.write(f"- [{d.id} - {d.callsign}] Role: {d.role}\n")
                f.write(f"  * Flown Distance       : {d.total_distance_flown:.1f} m\n")
                f.write(f"  * Energy Consumed      : {d.total_energy_wh:.2f} Wh\n")
                f.write(f"  * Final Battery SoC    : {d.soc_pct:.1f}% (Voltage: {d.voltage:.2f} V)\n")
                f.write(f"  * Battery State-of-Health: {d.pdm.soh_pct:.2f}%\n")
                f.write(f"  * Final Peak Temp      : {d.pdm.motor_temp_c:.1f} °C\n")
                f.write(f"  * Mean Vibration       : {d.pdm.vibration_g:.3f} g\n")

            f.write("\n2. AIRSPACE DECONFLICTION & SAFETY ASSURANCE\n")
            f.write("--------------------------------------------------------------------------------\n")
            f.write(f"- Minimum Inter-UAV Separation: {self.min_separation_recorded:.2f} metres (Safe Limit: 10.0 m)\n")
            f.write(f"- Separation Safety Status    : {'SECURE - NO CONFLICTS' if self.min_separation_recorded >= 10.0 else 'VIOLATION DETECTED'}\n")
            f.write(f"- Altitude Stratification     : Layer 1 (20m), Layer 2 (30m), Layer 3 (15m)\n")

            f.write("\n3. CLOUD & IOT COMMUNICATION PERFORMANCE\n")
            f.write("--------------------------------------------------------------------------------\n")
            f.write(f"- Total Telemetry Published   : {self.broker.published_messages} messages\n")
            f.write(f"- Ingestion Reliability Rate   : {(self.broker.delivered_messages / self.broker.published_messages * 100.0):.2f}%\n")
            mean_latency = np.mean(self.broker.latencies_ms) if self.broker.latencies_ms else 25.0
            f.write(f"- Average Edge-to-Cloud Latency: {mean_latency:.1f} ms\n")
            f.write(f"- Condition Alerts Emitted    : {len(self.broker.alerts)} events\n")

            f.write("\n4. SUSTAINABILITY & CARBON OFFSET ANALYSIS\n")
            f.write("--------------------------------------------------------------------------------\n")
            f.write(f"- Total Fleet Distance Flown  : {total_flown_km:.3f} km\n")
            f.write(f"- Total Electrical Energy Used: {total_energy_kwh:.4f} kWh ({total_energy_kwh / total_flown_km * 1000.0:.1f} Wh/km)\n")
            f.write(f"- Electric Fleet CO2 Footprint: {electric_fleet_co2_kg:.4f} kg CO2\n")
            f.write(f"- Baseline Diesel Van CO2     : {equivalent_diesel_co2_kg:.4f} kg CO2\n")
            f.write(f"- Net Carbon Emissions Saved  : {co2_saved_kg:.4f} kg CO2 ({carbon_reduction_pct:.1f}% reduction)\n")
            f.write("================================================================================\n")

        print(f"Saved executive summary report to: {output_path}")


    # ==========================================================================
    # 7. VISUALIZATIONS GENERATOR
    # ==========================================================================
    def generate_all_dashboards(self, output_dir: str):
        colors = {"UAV-Alpha": "#1976D2", "UAV-Bravo": "#D32F2F", "UAV-Charlie": "#2E7D32"}

        # ----------------------------------------------------------------------
        # Figure 1: 2D Multi-UAV Tracking & Deconfliction Map
        # ----------------------------------------------------------------------
        print("Generating Figure 1: 2D Fleet Tracking Map ...")
        fig, ax = plt.subplots(figsize=(11, 8.5), dpi=150)

        for drone in self.fleet:
            c = colors[drone.id]
            xs = [r["x_m"] for r in drone.history]
            ys = [r["y_m"] for r in drone.history]
            wpx = [wp["x_m"] for wp in drone.waypoints]
            wpy = [wp["y_m"] for wp in drone.waypoints]

            # Corridor setpoints
            ax.plot(wpx, wpy, linestyle="--", color=c, alpha=0.5, linewidth=1.5, label=f"{drone.id} Corridor")
            # Flown trajectory
            ax.plot(xs, ys, linestyle="-", color=c, linewidth=2.2, label=f"{drone.id} ({drone.callsign})")
            # Waypoint markers
            ax.scatter(wpx, wpy, color=c, s=40, zorder=4)
            # Launch / Pad marker
            ax.scatter(wpx[0], wpy[0], color=c, marker="s", s=90, edgecolors="black", zorder=5)

            # Sample safety separation buffer circles (every 100th step)
            for idx in range(10, len(xs), 120):
                circle = plt.Circle((xs[idx], ys[idx]), 10.0, color=c, fill=False, linestyle=":", alpha=0.35)
                ax.add_patch(circle)

        ax.set_title("Enterprise UAV Fleet Tracking & Geospatial Airspace Corridor Map", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Local East Coordinate (metres)", fontsize=11)
        ax.set_ylabel("Local North Coordinate (metres)", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper left", framealpha=0.92, fontsize=9)
        plt.tight_layout()
        fig1_path = os.path.join(output_dir, "fleet_tracking_2d.png")
        fig.savefig(fig1_path)
        plt.close(fig)
        print(f"  -> Saved: {fig1_path}")

        # ----------------------------------------------------------------------
        # Figure 2: 3D Airspace Deconfliction & Layered Trajectory
        # ----------------------------------------------------------------------
        print("Generating Figure 2: 3D Airspace Trajectory ...")
        fig = plt.figure(figsize=(11, 8.5), dpi=150)
        ax3d = fig.add_subplot(111, projection="3d")

        for drone in self.fleet:
            c = colors[drone.id]
            xs = [r["x_m"] for r in drone.history]
            ys = [r["y_m"] for r in drone.history]
            zs = [r["z_m"] for r in drone.history]

            # 3D trajectory
            ax3d.plot(xs, ys, zs, color=c, linewidth=2.4, label=f"{drone.id} [Target Alt: {drone.target_alt}m]")
            # Ground projection
            ax3d.plot(xs, ys, [0.0]*len(xs), color="#757575", linestyle=":", alpha=0.45)

        ax3d.set_title("3D Airspace Corridor Deconfliction & Stratification View", fontsize=13, fontweight="bold", pad=14)
        ax3d.set_xlabel("East X (m)", labelpad=8)
        ax3d.set_ylabel("North Y (m)", labelpad=8)
        ax3d.set_zlabel("Altitude Z (m)", labelpad=8)
        ax3d.set_zlim(0, 35)
        ax3d.view_init(elev=28, azim=-62)
        ax3d.legend(loc="upper right", framealpha=0.9, fontsize=9)
        plt.tight_layout()
        fig2_path = os.path.join(output_dir, "fleet_trajectory_3d.png")
        fig.savefig(fig2_path)
        plt.close(fig)
        print(f"  -> Saved: {fig2_path}")

        # ----------------------------------------------------------------------
        # Figure 3: Predictive Maintenance Dashboard
        # ----------------------------------------------------------------------
        print("Generating Figure 3: Predictive Maintenance Dashboard ...")
        fig, axes = plt.subplots(2, 2, figsize=(14, 9), dpi=150)
        fig.suptitle("Enterprise Fleet Predictive Maintenance & Health Telemetry", fontsize=15, fontweight="bold", y=0.98)

        times = [r["timestamp_s"] for r in self.fleet[0].history]

        # Subplot 1: Motor Bearing Vibration
        ax1 = axes[0, 0]
        for drone in self.fleet:
            d_times = [r["timestamp_s"] for r in drone.history]
            vibs = [r["vibration_g"] for r in drone.history]
            ax1.plot(d_times, vibs, color=colors[drone.id], linewidth=1.8, label=f"{drone.id}")
        ax1.axhline(0.85, color="#D32F2F", linestyle="--", linewidth=1.2, label="Wear Warning Threshold (0.85g)")
        ax1.set_title("1. Motor Bearing Vibration Spectrum (RMS g)", fontweight="bold", fontsize=11)
        ax1.set_xlabel("Mission Time (s)")
        ax1.set_ylabel("Vibration (g)")
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend(loc="upper left", fontsize=8, framealpha=0.9)

        # Subplot 2: Motor Winding Thermal Profile
        ax2 = axes[0, 1]
        for drone in self.fleet:
            d_times = [r["timestamp_s"] for r in drone.history]
            temps = [r["motor_temp_c"] for r in drone.history]
            ax2.plot(d_times, temps, color=colors[drone.id], linewidth=1.8, label=f"{drone.id}")
        ax2.axhline(55.0, color="#FF9800", linestyle="--", linewidth=1.2, label="Thermal Alert Limit (55°C)")
        ax2.set_title("2. Motor Winding Temperature Dynamics (°C)", fontweight="bold", fontsize=11)
        ax2.set_xlabel("Mission Time (s)")
        ax2.set_ylabel("Temperature (°C)")
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend(loc="upper left", fontsize=8, framealpha=0.9)

        # Subplot 3: Battery State-of-Health & Internal Resistance
        ax3 = axes[1, 0]
        for drone in self.fleet:
            d_times = [r["timestamp_s"] for r in drone.history]
            res_mohm = [r["internal_res_ohm"] * 1000.0 for r in drone.history]
            ax3.plot(d_times, res_mohm, color=colors[drone.id], linewidth=1.8, label=f"{drone.id} (R_int)")
        ax3.set_title("3. Battery Internal Resistance Drift (mΩ)", fontweight="bold", fontsize=11)
        ax3.set_xlabel("Mission Time (s)")
        ax3.set_ylabel("Internal Resistance (mΩ)")
        ax3.grid(True, linestyle="--", alpha=0.5)
        ax3.legend(loc="upper left", fontsize=8, framealpha=0.9)

        # Subplot 4: Health Index & Event Alert Distribution
        ax4 = axes[1, 1]
        alert_severities = [a["severity"] for a in self.broker.alerts]
        categories = ["INFO", "WARNING", "ALERT", "CRITICAL"]
        counts = [alert_severities.count(c) for c in categories]
        bar_colors = ["#2196F3", "#FF9800", "#F44336", "#9C27B0"]
        bars = ax4.bar(categories, counts, color=bar_colors, width=0.55, edgecolor="black")
        for bar in bars:
            yval = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, int(yval), ha="center", va="bottom", fontweight="bold")
        ax4.set_title("4. Condition-Based Maintenance Alerts Logged", fontweight="bold", fontsize=11)
        ax4.set_ylabel("Incident Frequency Count")
        ax4.set_ylim(0, max(counts + [3]) + 1.5)
        ax4.grid(axis="y", linestyle="--", alpha=0.5)

        plt.tight_layout()
        fig3_path = os.path.join(output_dir, "predictive_maintenance_dashboard.png")
        fig.savefig(fig3_path)
        plt.close(fig)
        print(f"  -> Saved: {fig3_path}")

        # ----------------------------------------------------------------------
        # Figure 4: Enterprise Fleet Operations Master Dashboard
        # ----------------------------------------------------------------------
        print("Generating Figure 4: Fleet Operations Dashboard ...")
        fig, axes = plt.subplots(3, 2, figsize=(15, 12), dpi=150)
        fig.suptitle("Enterprise Autonomous UAV Fleet Operations Command Center", fontsize=16, fontweight="bold", y=0.99)

        # Panel 1: Fleet Altitude Profiles
        p1 = axes[0, 0]
        for drone in self.fleet:
            d_times = [r["timestamp_s"] for r in drone.history]
            alts = [r["z_m"] for r in drone.history]
            p1.plot(d_times, alts, color=colors[drone.id], linewidth=2.0, label=f"{drone.id} ({drone.role[:14]}...)")
        p1.set_title("1. Coordinated Fleet Altitude Layering", fontweight="bold", fontsize=11)
        p1.set_xlabel("Time (s)")
        p1.set_ylabel("Altitude (m)")
        p1.grid(True, linestyle="--", alpha=0.5)
        p1.legend(loc="upper right", fontsize=8, framealpha=0.9)

        # Panel 2: Ground Speed
        p2 = axes[0, 1]
        for drone in self.fleet:
            d_times = [r["timestamp_s"] for r in drone.history]
            speeds = [r["speed_mps"] for r in drone.history]
            p2.plot(d_times, speeds, color=colors[drone.id], linewidth=1.8, label=f"{drone.id}")
        p2.set_title("2. Fleet Ground Speed Profiles (m/s)", fontweight="bold", fontsize=11)
        p2.set_xlabel("Time (s)")
        p2.set_ylabel("Speed (m/s)")
        p2.grid(True, linestyle="--", alpha=0.5)
        p2.legend(loc="lower right", fontsize=8, framealpha=0.9)

        # Panel 3: Battery State of Charge
        p3 = axes[1, 0]
        for drone in self.fleet:
            d_times = [r["timestamp_s"] for r in drone.history]
            socs = [r["soc_pct"] for r in drone.history]
            p3.plot(d_times, socs, color=colors[drone.id], linewidth=2.0, label=f"{drone.id} SoC")
        p3.set_title("3. Battery State-of-Charge Depletion (%)", fontweight="bold", fontsize=11)
        p3.set_xlabel("Time (s)")
        p3.set_ylabel("SoC (%)")
        p3.set_ylim(80, 102)
        p3.grid(True, linestyle="--", alpha=0.5)
        p3.legend(loc="lower left", fontsize=8, framealpha=0.9)

        # Panel 4: Airspace Separation Distance
        p4 = axes[1, 1]
        t_sep = self.time_history[:len(self.separation_history)]
        sep_ab = [s[0] for s in self.separation_history]
        sep_bc = [s[1] for s in self.separation_history]
        sep_ac = [s[2] for s in self.separation_history]
        p4.plot(t_sep, sep_ab, color="#7B1FA2", linewidth=1.6, label="Dist: Alpha - Bravo")
        p4.plot(t_sep, sep_bc, color="#0097A7", linewidth=1.6, label="Dist: Bravo - Charlie")
        p4.plot(t_sep, sep_ac, color="#F57C00", linewidth=1.6, label="Dist: Alpha - Charlie")
        p4.axhline(10.0, color="#D32F2F", linestyle="--", linewidth=1.4, label="Safe Separation Limit (10m)")
        p4.set_title("4. Inter-UAV Spatial Separation Assurance", fontweight="bold", fontsize=11)
        p4.set_xlabel("Time (s)")
        p4.set_ylabel("Separation (m)")
        p4.grid(True, linestyle="--", alpha=0.5)
        p4.legend(loc="upper right", fontsize=8, framealpha=0.9)

        # Panel 5: IoT Cloud Communication Latency
        p5 = axes[2, 0]
        lat_samples = self.broker.latencies_ms
        t_lat = np.linspace(0, self.time_history[-1], len(lat_samples)) if lat_samples else []
        if len(t_lat) > 0:
            p5.plot(t_lat, lat_samples, color="#00796B", linewidth=0.6, alpha=0.65, label="Edge MQTT Packet Latency")
            p5.axhline(np.mean(lat_samples), color="#E65100", linestyle="-", linewidth=1.5, label=f"Mean Latency ({np.mean(lat_samples):.1f} ms)")
        p5.set_title("5. IoT Edge-to-Cloud Messaging Latency (ms)", fontweight="bold", fontsize=11)
        p5.set_xlabel("Time (s)")
        p5.set_ylabel("Latency (ms)")
        p5.grid(True, linestyle="--", alpha=0.5)
        p5.legend(loc="upper right", fontsize=8, framealpha=0.9)

        # Panel 6: Sustainability & Carbon Offset Comparison
        p6 = axes[2, 1]
        total_flown_km = sum(d.total_distance_flown for d in self.fleet) / 1000.0
        total_energy_kwh = sum(d.total_energy_wh for d in self.fleet) / 1000.0
        electric_fleet_co2_kg = total_energy_kwh * GRID_EMISSION_KG_PER_KWH
        equivalent_diesel_co2_kg = total_flown_km * (DIESEL_EMISSION_G_PER_KM / 1000.0)

        modes = ["Diesel Delivery Van", "Electric UAV Fleet"]
        emissions = [equivalent_diesel_co2_kg, electric_fleet_co2_kg]
        colors_bar = ["#78909C", "#43A047"]
        b_bars = p6.bar(modes, emissions, color=colors_bar, width=0.5, edgecolor="black")
        for b in b_bars:
            h = b.get_height()
            p6.text(b.get_x() + b.get_width()/2.0, h + 0.005, f"{h:.4f} kg", ha="center", va="bottom", fontweight="bold")
        p6.set_title("6. Sustainability: Fleet Carbon Footprint Offset", fontweight="bold", fontsize=11)
        p6.set_ylabel("CO2 Emissions (kg)")
        p6.set_ylim(0, max(emissions) * 1.35)
        p6.grid(axis="y", linestyle="--", alpha=0.5)

        plt.tight_layout()
        fig4_path = os.path.join(output_dir, "fleet_operations_dashboard.png")
        fig.savefig(fig4_path)
        plt.close(fig)
        print(f"  -> Saved: {fig4_path}")


# ==============================================================================
# 8. MAIN ENTRYPOINT
# ==============================================================================
def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mission_file = os.path.join(base_dir, "fleet_mission_plan.json")
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    sim = FleetSimulationManager(mission_file)
    sim.run(dt=0.1, max_duration_s=85.0)

    # Export deliverables
    sim.export_telemetry_csv(os.path.join(results_dir, "fleet_telemetry.csv"))
    sim.export_alerts_json(os.path.join(results_dir, "fleet_alerts_log.json"))
    sim.export_summary_report(os.path.join(results_dir, "fleet_performance_summary.txt"))
    sim.generate_all_dashboards(results_dir)

    print("\nAll Level 3 Enterprise UAV Fleet simulation files successfully generated!")


if __name__ == "__main__":
    main()
