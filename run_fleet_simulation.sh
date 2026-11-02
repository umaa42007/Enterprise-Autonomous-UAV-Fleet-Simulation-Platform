#!/bin/bash
# ==============================================================================
# Enterprise Autonomous UAV Fleet Simulation Platform (Level 3 - Advanced)
# Execution Launcher Script
# ==============================================================================

set -e

# Resolve directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "================================================================================"
echo " Starting Enterprise Autonomous UAV Fleet Simulation Platform (Level 3)"
echo "================================================================================"

# Check for virtual environment
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "[INFO] Activating virtual environment..."
    source "$SCRIPT_DIR/venv/bin/activate"
    PYTHON_CMD="python3"
else
    echo "[INFO] Using system Python 3..."
    PYTHON_CMD="python3"
fi

# Verify Python version
$PYTHON_CMD -c "import sys; print(f'[INFO] Python version: {sys.version.split()[0]}')"

# Run simulation
echo "[INFO] Executing uav_fleet_simulation.py..."
$PYTHON_CMD "$SCRIPT_DIR/uav_fleet_simulation.py"

echo "================================================================================"
echo " Simulation Complete! Generated Outputs in: $SCRIPT_DIR/results/"
echo " - 2D Fleet Tracking Map     : results/fleet_tracking_2d.png"
echo " - 3D Airspace Trajectory    : results/fleet_trajectory_3d.png"
echo " - Predictive Maintenance    : results/predictive_maintenance_dashboard.png"
echo " - Fleet Operations Dashboard: results/fleet_operations_dashboard.png"
echo " - Fleet Telemetry Dataset   : results/fleet_telemetry.csv"
echo " - Condition Alerts Log      : results/fleet_alerts_log.json"
echo " - Executive Performance Rpt : results/fleet_performance_summary.txt"
echo "================================================================================"
