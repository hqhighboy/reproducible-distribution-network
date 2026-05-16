"""Analysis helpers for simulated distribution-network results."""

from __future__ import annotations

import logging
from statistics import mean
from typing import Any

from .model import NetworkModel

logger = logging.getLogger(__name__)


def analyze_results(
    network: NetworkModel,
    simulation_results: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Compute simple reproducibility metrics from the dummy simulation."""
    logger.info("Analyzing voltage profile and benchmark indicators...")

    limits = config.get("simulation", {}).get("voltage_limits_pu", {})
    lower = float(limits.get("lower", 0.95))
    upper = float(limits.get("upper", 1.05))
    voltages = simulation_results["voltage_profile_pu"]

    violating_buses = [
        bus for bus, voltage in voltages.items() if voltage < lower or voltage > upper
    ]
    summary = {
        "network": network.name,
        "bus_count": len(network.buses),
        "min_voltage_pu": min(voltages.values()),
        "max_voltage_pu": max(voltages.values()),
        "mean_voltage_pu": round(mean(voltages.values()), 4),
        "voltage_violation_count": len(violating_buses),
        "violating_buses": violating_buses,
    }
    logger.info("Analysis complete: %s voltage violations.", len(violating_buses))
    return summary
