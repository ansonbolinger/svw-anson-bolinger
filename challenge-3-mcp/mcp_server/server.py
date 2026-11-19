"""Custom MCP Server built with FastMCP for Challenge 3.

Exposes custom system diagnostics, arithmetic calculations, and text transformations
as agent-ready tools conforming to the Model Context Protocol (MCP).
"""

from mcp.server.fastmcp import FastMCP
import platform
import datetime

# Create the FastMCP server instance
mcp = FastMCP("custom-diagnostics-server")


@mcp.tool()
def get_system_diagnostics() -> str:
    """Returns local system diagnostics, architecture, OS platform, and current timestamp."""
    info = {
        "os": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "OPERATIONAL"
    }
    return (
        f"System Status: {info['status']}\n"
        f"Operating System: {info['os']} {info['release']} ({info['architecture']})\n"
        f"Python Runtime: {info['python_version']}\n"
        f"Current UTC Time: {info['timestamp_utc']}"
    )


@mcp.tool()
def calculate_resource_budget(num_nodes: int, ram_gb_per_node: float, cpu_cores_per_node: int) -> str:
    """Calculates cluster computing resources and estimated monthly cloud cost.

    Args:
        num_nodes: Number of compute nodes in the cluster.
        ram_gb_per_node: RAM in gigabytes per node.
        cpu_cores_per_node: Number of vCPU cores per node.

    Returns:
        A breakdown of total vCPUs, total RAM (GB), and estimated monthly cost in USD.
    """
    total_cores = num_nodes * cpu_cores_per_node
    total_ram = num_nodes * ram_gb_per_node
    # Estimated standard cloud rates: $0.035 per core-hour, $0.0045 per GB-hour
    hourly_rate = (total_cores * 0.035) + (total_ram * 0.0045)
    monthly_rate = hourly_rate * 730

    return (
        f"Cluster Capacity for {num_nodes} node(s):\n"
        f"- Total Compute: {total_cores} vCPU cores\n"
        f"- Total Memory: {total_ram:.1f} GB RAM\n"
        f"- Estimated Hourly Cost: ${hourly_rate:.2f}\n"
        f"- Estimated Monthly Cost: ${monthly_rate:.2f} USD"
    )


@mcp.tool()
def transform_identifier(text: str, format_type: str = "kebab") -> str:
    """Transforms a string into standardized code identifiers (kebab-case, snake_case, or camelCase).

    Args:
        text: The input text to convert.
        format_type: Format to convert into: 'kebab', 'snake', or 'camel'. Default is 'kebab'.

    Returns:
        The formatted identifier string.
    """
    words = [w.strip() for w in text.replace("-", " ").replace("_", " ").split() if w.strip()]
    if not words:
        return text

    if format_type.lower() == "snake":
        return "_".join(words).lower()
    elif format_type.lower() == "camel":
        return words[0].lower() + "".join(w.capitalize() for w in words[1:])
    else:  # default kebab
        return "-".join(words).lower()


if __name__ == "__main__":
    mcp.run()
