"""ADS Legacy Backend Mock Server using FastMCP.

Simulates the Alaska Department of Snow real-time telemetry, plow fleet dispatch,
and highway sensor readings.
"""

from mcp.server.fastmcp import FastMCP
import datetime

mcp = FastMCP("ads-backend-mcp-server")

# Simulated live state of plow units
PLOW_FLEET = {
    "PLOW-ALPHA-01": {"location": "Parks Hwy MP 45", "status": "ACTIVE_PLOWING", "fuel": "82%", "driver": "J. Miller"},
    "PLOW-ALPHA-04": {"location": "Glenn Hwy MP 18", "status": "ACTIVE_SALTING", "fuel": "64%", "driver": "S. Kowalski"},
    "BLOWER-BRAVO-02": {"location": "Thompson Pass MP 26", "status": "CLEARING_DRIFT", "fuel": "91%", "driver": "E. Lindgren"},
    "BLOWER-BRAVO-05": {"location": "Turnagain Pass MP 63", "status": "STAGED_STANDBY", "fuel": "95%", "driver": "K. Adams"},
    "SPREADER-CHARLIE-03": {"location": "Seward Hwy MP 88", "status": "DISPERSING_BRINE", "fuel": "55%", "driver": "M. Vance"},
}

HIGHWAY_SENSORS = {
    "SEWARD-HWY-MP60": {"pass": "Turnagain Pass", "temp_f": 14, "wind_mph": 38, "snow_accum_in": 11.5, "avalanche_risk": "HIGH", "status": "AMBER_DIFFICULT"},
    "RICHARDSON-HWY-MP28": {"pass": "Thompson Pass", "temp_f": 6, "wind_mph": 52, "snow_accum_in": 24.0, "avalanche_risk": "EXTREME", "status": "RED_CLOSED"},
    "PARKS-HWY-MP135": {"pass": "Broad Pass", "temp_f": -2, "wind_mph": 22, "snow_accum_in": 6.0, "avalanche_risk": "MODERATE", "status": "AMBER_DIFFICULT"},
    "GLENN-HWY-MP35": {"pass": "Palmer Corridor", "temp_f": 20, "wind_mph": 15, "snow_accum_in": 3.0, "avalanche_risk": "LOW", "status": "GREEN_NORMAL"},
}


@mcp.tool()
def get_highway_sensor_status(highway_code: str) -> str:
    """Queries live telemetry, pavement temperature, wind speed, and snow accumulation from roadside sensors.

    Args:
        highway_code: Name or fragment of highway (e.g., 'Seward', 'Richardson', 'Thompson Pass', 'Parks').

    Returns:
        Structured sensor telemetry and road condition summary.
    """
    code = highway_code.lower().strip()
    matches = []
    for sensor_id, data in HIGHWAY_SENSORS.items():
        if code in sensor_id.lower() or code in data["pass"].lower():
            matches.append(
                f"- Sensor {sensor_id} ({data['pass']}): Pavement Temp: {data['temp_f']}°F, "
                f"Wind: {data['wind_mph']} mph, Accumulation: {data['snow_accum_in']} in, "
                f"Avalanche Risk: {data['avalanche_risk']}, Road Status: {data['status']}"
            )
    if not matches:
        return f"No sensors found matching '{highway_code}'. Available corridors: Seward, Richardson/Thompson Pass, Parks, Glenn."
    return "Alaska Highway Sensor Telemetry:\n" + "\n".join(matches)


@mcp.tool()
def dispatch_plow_unit(unit_id: str, target_location: str, action: str) -> str:
    """Dispatches an ADS heavy plow, rotary snow blower, or chemical spreader to an emergency location.

    Args:
        unit_id: Identifier of the unit (e.g., 'PLOW-ALPHA-01', 'BLOWER-BRAVO-02').
        target_location: Highway name and milepost destination (e.g. 'Thompson Pass MP 28').
        action: Operational directive (e.g. 'PLOW_CORRIDOR', 'AVALANCHE_CLEAR', 'DEICE_BRINE').

    Returns:
        Confirmation of dispatch order, assigned crew, and estimated arrival time.
    """
    unit_id_clean = unit_id.upper().strip()
    unit = PLOW_FLEET.get(unit_id_clean)
    if not unit:
        avail = ", ".join(PLOW_FLEET.keys())
        return f"Unit '{unit_id}' not found in active fleet. Available units: {avail}"

    unit["location"] = target_location
    unit["status"] = action.upper()

    return (
        f"DISPATCH CONFIRMED:\n"
        f"- Unit: {unit_id_clean} ({unit['driver']})\n"
        f"- Target Destination: {target_location}\n"
        f"- Assigned Action: {action.upper()}\n"
        f"- Current Unit Fuel: {unit['fuel']}\n"
        f"- Status: EN_ROUTE / DISPATCHED (Priority Signal Enabled)"
    )


@mcp.tool()
def get_fleet_readiness() -> str:
    """Returns the operational status, current location, and fuel level of all active ADS plow and blower units."""
    lines = []
    for uid, data in PLOW_FLEET.items():
        lines.append(f"- {uid}: {data['status']} at {data['location']} (Fuel: {data['fuel']}, Driver: {data['driver']})")
    return "ADS Active Fleet Readiness:\n" + "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
