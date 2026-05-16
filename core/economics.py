"""Economic post-processing for the reproducibility demo."""

from __future__ import annotations

import logging
from typing import Any

from .model import NetworkModel

logger = logging.getLogger(__name__)


def evaluate_economics(
    network: NetworkModel,
    simulation_results: dict[str, Any],
    analysis_results: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate deterministic placeholder economic indicators."""
    logger.info("Evaluating economic indicators...")

    economics = config.get("economics", {})
    energy_price = float(economics.get("energy_price_per_kwh", 0.10))
    annual_hours = int(economics.get("annual_hours", 8760))
    currency = str(economics.get("currency", "USD"))

    annual_loss_cost = simulation_results["line_losses_kw"] * annual_hours * energy_price
    transformer_capacity = sum(int(item.get("capacity_kva", 0)) for item in network.transformers)
    annualized_equipment_cost = transformer_capacity * 4.0

    summary = {
        "currency": currency,
        "annual_loss_cost": round(annual_loss_cost, 2),
        "annualized_equipment_cost": round(annualized_equipment_cost, 2),
        "voltage_violation_penalty": analysis_results["voltage_violation_count"] * 1000.0,
        "total_placeholder_cost": round(
            annual_loss_cost
            + annualized_equipment_cost
            + analysis_results["voltage_violation_count"] * 1000.0,
            2,
        ),
    }
    logger.info("Economic evaluation complete: %.2f %s total placeholder cost.", summary["total_placeholder_cost"], currency)
    return summary
