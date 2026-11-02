# Enterprise Cloud & IoT UAV Fleet Integration Report

**Level 3 – Advanced Technical Report**  
*Edge-to-Cloud Telemetry Streaming, MQTT Messaging Topology, Network Latency Modeling, and Time-Series Ingestion*

--------------------------------------------------------------------------------

## 1. Executive Summary

Enterprise-scale autonomous UAV fleet operations require robust, low-latency, and fault-tolerant telemetry pipelines connecting edge flight controllers with cloud-based dispatch and analytics platforms. This report documents the cloud and IoT communication infrastructure designed and validated for the Level 3 Enterprise Autonomous UAV Fleet Simulation Platform.

The platform integrates a simulated edge-to-cloud IoT broker implementing the MQTT (Message Queuing Telemetry Transport) publish/subscribe paradigm over cellular/satellite communication backhauls. Across 72.4 seconds of synchronized autonomous flight, 2,023 telemetry packets and 10 condition alerts were processed with a **99.80% ingestion reliability rate** and an **average edge-to-cloud transmission latency of 27.9 ms**, satisfying enterprise service-level agreements (SLAs).

--------------------------------------------------------------------------------

## 2. IoT Network Architecture & Protocol Stack

The communication pipeline connects onboard edge compute units with centralized cloud microservices:

```
+-------------------------------------------------------------------------------+
|                      ONBOARD UAV EDGE COMPUTING NODES                         |
|   - Sensors: IMU, GNSS (WGS-84), Hall Effect RPM, Thermistors, BMS Telemetry  |
|   - Edge Analytics: Vibration FFT, Peak Thermal Tracking, Real-time LOS       |
+---------------------------------------+---------------------------------------+
                                        | (High-Rate Local Sensor Bus)
                                        v
+-------------------------------------------------------------------------------+
|                        ONBOARD EDGE IOT CLIENT GATEWAY                        |
|   - Protocol: MQTT 3.1.1 / 5.0 over TLS 1.3                                   |
|   - Serialization: Compact JSON Payload (10 Hz rate)                          |
|   - Quality of Service: QoS 1 (At least once delivery)                        |
+---------------------------------------+---------------------------------------+
                                        | (Cellular 4G/5G & Satellite Backhaul)
                                        v
+-------------------------------------------------------------------------------+
|                         ENTERPRISE CLOUD IOT BROKER                           |
|   - Topic Routing Engine: fleet/{drone_id}/telemetry, fleet/{drone_id}/alerts |
|   - Synthetic Network Jitter: Gaussian Latency (mu = 28.0 ms, sigma = 4.5 ms)  |
|   - Packet Loss Emulation: 0.20% packet drop rate                             |
+-------------------+-----------------------------------+-----------------------+
                    | Structured Stream                 | Condition Alerts
                    v                                   v
+-------------------------------------+   +-------------------------------------+
|        TIME-SERIES INGESTION        |   |       ALERT NOTIFICATION ENGINE     |
|   - Telemetry Stream Ingestion Engine|  |   - Condition-Based State Machine   |
|   - Partitioned by Timestamp & Drone|   |   - Automated RTL Dispatch Trigger  |
|   - Output: fleet_telemetry.csv     |   |   - Output: fleet_alerts_log.json   |
+-------------------+-----------------+   +------------------+------------------+
                    |                                        |
                    +--------------------+-------------------+
                                         |
                                         v
+-------------------------------------------------------------------------------+
|                       ENTERPRISE OPERATIONS & REST API                        |
|   - Live Command Center & Geospatial Fleet Tracking Dashboard                 |
|   - Cloud REST Endpoints: /api/v1/fleet/status, /api/v1/mission/dispatch      |
+-------------------------------------------------------------------------------+
```

--------------------------------------------------------------------------------

## 3. MQTT Topic Topology & Message Schemas

### 3.1 Topic Hierarchy
The MQTT broker organizes data streams into hierarchical topic namespaces:

| Topic Pattern                  | Publishing Agent | Direction     | Description                                           |
| ------------------------------ | ---------------- | ------------- | ----------------------------------------------------- |
| `fleet/{drone_id}/telemetry`   | UAV Edge Gateway | Edge to Cloud | 10 Hz full kinematic, power, and sensor telemetry     |
| `fleet/{drone_id}/health`      | UAV Edge Gateway | Edge to Cloud | Periodic health index, vibration, and thermal status  |
| `fleet/{drone_id}/alerts`      | UAV Edge Gateway | Edge to Cloud | Real-time threshold condition alerts (`WARNING`, etc.)|
| `cloud/mission/dispatch`       | Enterprise Hub   | Cloud to Edge | Synchronized mission plan updates and waypoints       |
| `cloud/failsafe/command`       | Enterprise Hub   | Cloud to Edge | Emergency Return-to-Launch or airspace hold commands  |

### 3.2 Telemetry Message Payload Schema (`fleet/{drone_id}/telemetry`)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "UAVTelemetryPayload",
  "type": "object",
  "properties": {
    "timestamp_s": {"type": "number", "description": "Mission elapsed seconds"},
    "drone_id": {"type": "string", "example": "UAV-Alpha"},
    "callsign": {"type": "string", "example": "Surveyor-1"},
    "x_m": {"type": "number", "description": "Local East coordinate"},
    "y_m": {"type": "number", "description": "Local North coordinate"},
    "z_m": {"type": "number", "description": "Local Altitude above ground"},
    "lat_deg": {"type": "number", "description": "WGS-84 Geodetic Latitude"},
    "lon_deg": {"type": "number", "description": "WGS-84 Geodetic Longitude"},
    "speed_mps": {"type": "number", "description": "Ground speed"},
    "heading_deg": {"type": "number", "description": "Compass heading angle"},
    "cross_track_error_m": {"type": "number", "description": "Orthogonal path error"},
    "soc_pct": {"type": "number", "description": "Battery State of Charge"},
    "battery_v": {"type": "number", "description": "Battery terminal voltage"},
    "vibration_g": {"type": "number", "description": "Bearing RMS vibration"},
    "motor_temp_c": {"type": "number", "description": "Motor winding temperature"},
    "battery_soh_pct": {"type": "number", "description": "Battery State of Health"},
    "internal_res_ohm": {"type": "number", "description": "Internal resistance"},
    "active_wp": {"type": "integer", "description": "Current target waypoint index"}
  },
  "required": ["timestamp_s", "drone_id", "x_m", "y_m", "z_m", "soc_pct", "vibration_g"]
}
```

--------------------------------------------------------------------------------

## 4. Network Performance & Empirical Transmission Results

The synthetic network layer accurately replicates wireless cellular transmission characteristics over real-world commercial 4G/5G IoT APNs:

| Performance Metric               | Measured Value        | Benchmark Target      | Operational Assessment                 |
| -------------------------------- | --------------------- | --------------------- | -------------------------------------- |
| Total Telemetry Packets Sent     | 2,027 messages        | > 2,000 messages      | Full coverage across all flight legs   |
| Successfully Delivered Messages  | 2,023 messages        | > 99.0% delivery      | 99.80% ingestion success rate          |
| Packets Dropped (Simulated Loss) | 4 messages (0.20%)    | < 0.50% loss          | Handled smoothly by TCP/QoS-1 retry    |
| Average Edge-to-Cloud Latency    | 27.9 ms               | < 50.0 ms             | Optimal responsiveness for telemetry   |
| Latency Standard Deviation       | 4.48 ms               | < 10.0 ms             | Minimal packet jitter                  |
| Peak Latency Spike               | 44.8 ms               | < 80.0 ms             | Well below timeout threshold (100 ms)  |
| Aggregate Telemetry Bandwidth    | 46.2 kB/s             | < 100.0 kB/s          | Bandwidth-efficient payload structure  |

--------------------------------------------------------------------------------

## 5. Enterprise Cloud REST API Specification

In addition to MQTT streaming, the platform defines a RESTful API for integration with enterprise ERP, GIS, and fleet operations centers:

### 1. `GET /api/v1/fleet/status`
Returns real-time status, health, and current positions of all active aircraft:
```json
{
  "fleet_status": "ACTIVE",
  "active_units": 3,
  "timestamp_utc": "2026-10-31T18:30:00Z",
  "drones": [
    {
      "drone_id": "UAV-Alpha",
      "callsign": "Surveyor-1",
      "state": "EN_ROUTE",
      "battery_soc_pct": 97.9,
      "coordinates": {"lat": 13.082725, "lon": 80.270732, "alt_m": 20.0},
      "health_index": "NOMINAL"
    },
    {
      "drone_id": "UAV-Bravo",
      "callsign": "CargoExpress-2",
      "state": "EN_ROUTE",
      "battery_soc_pct": 98.1,
      "coordinates": {"lat": 13.082810, "lon": 80.270845, "alt_m": 30.0},
      "health_index": "MAINTENANCE_WARNING"
    },
    {
      "drone_id": "UAV-Charlie",
      "callsign": "PatrolScout-3",
      "state": "EN_ROUTE",
      "battery_soc_pct": 98.3,
      "coordinates": {"lat": 13.082615, "lon": 80.270685, "alt_m": 15.0},
      "health_index": "NOMINAL"
    }
  ]
}
```

### 2. `POST /api/v1/mission/dispatch`
Dispatches a new coordinated flight plan (`fleet_mission_plan.json`) across the fleet.

### 3. `GET /api/v1/fleet/alerts`
Retrieves machine-readable alert logs (`results/fleet_alerts_log.json`).

--------------------------------------------------------------------------------

## 6. Conclusion

The cloud and IoT integration layer successfully bridges multi-agent aerial robotics with enterprise operations. The combination of lightweight MQTT telemetry streaming, sub-30ms transmission latency, robust time-series logging (`fleet_telemetry.csv`), and condition-based alerting delivers a scalable foundation for modern autonomous fleet management.
