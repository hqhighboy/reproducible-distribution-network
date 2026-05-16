"""Dummy power-flow simulation module."""

from __future__ import annotations

import logging
from typing import Any

from .model import NetworkModel

logger = logging.getLogger(__name__)


def run_power_flow(network: NetworkModel, config: dict[str, Any]) -> dict[str, Any]:
    """Run a deterministic placeholder power-flow simulation."""
    logger.info("Running power flow simulation...")

    load_scale = network.load_summary["load_scale"]
    voltage_profile = {}
    for idx, bus in enumerate(network.buses):
        voltage_drop = min(0.08, idx * 0.0025 * load_scale)
        voltage_profile[bus] = round(1.0 - voltage_drop, 4)

    total_kw = network.load_summary["total_kw"] * load_scale
    line_losses_kw = round(max(0.1, total_kw * 0.012), 3)

    results = {
        "method": config.get("simulation", {}).get("method", "dummy_power_flow"),
        "converged": True,
        "iterations": min(5, int(config.get("simulation", {}).get("max_iterations", 20))),
        "voltage_profile_pu": voltage_profile,
        "line_losses_kw": line_losses_kw,
        "served_load_kw": round(total_kw, 3),
    }
    logger.info("Power flow simulation complete: %.3f kW losses.", line_losses_kw)
    return results
