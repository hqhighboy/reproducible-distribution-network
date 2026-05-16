"""Network model construction for the reproducibility layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import logging
from typing import Any

logger = logging.getLogger(__name__)

STANDARD_10KV_TRANSFORMER_KVA = {50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630}


@dataclass(frozen=True)
class NetworkModel:
    """Lightweight network container used by the dummy workflow."""

    name: str
    feeder_type: str
    voltage_class_kv: float
    buses: list[str]
    line_count: int
    transformers: list[dict[str, Any]]
    load_summary: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


def build_network(config: dict[str, Any]) -> NetworkModel:
    """Build a minimal in-memory network model from a YAML configuration."""
    logger.info("Building network from config...")

    feeder = config.get("feeder", {})
    loads = config.get("loads", {})
    transformers = list(config.get("transformers", []))

    voltage_class_kv = float(feeder.get("voltage_class_kv", 0.0))
    if voltage_class_kv == 10.0:
        _validate_10kv_transformers(transformers)

    bus_count = int(feeder.get("bus_count", 0))
    buses = [f"bus_{idx:02d}" for idx in range(1, bus_count + 1)]

    model = NetworkModel(
        name=str(feeder.get("name", "unnamed_feeder")),
        feeder_type=str(feeder.get("type", "unknown")),
        voltage_class_kv=voltage_class_kv,
        buses=buses,
        line_count=int(feeder.get("line_count", max(bus_count - 1, 0))),
        transformers=transformers,
        load_summary={
            "total_kw": float(loads.get("total_kw", 0.0)),
            "total_kvar": float(loads.get("total_kvar", 0.0)),
            "load_scale": float(loads.get("load_scale", 1.0)),
        },
    )

    logger.info(
        "Network model ready: %s buses, %s lines, %s transformers.",
        len(model.buses),
        model.line_count,
        len(model.transformers),
    )
    return model


def _validate_10kv_transformers(transformers: list[dict[str, Any]]) -> None:
    """Guard the anonymized 10 kV feeder against unrealistic mock capacities."""
    for item in transformers:
        capacity = int(item.get("capacity_kva", 0))
        if capacity not in STANDARD_10KV_TRANSFORMER_KVA:
            raise ValueError(
                "10 kV transformer capacity must use a standard value between "
                f"50 and 630 kVA; got {capacity} kVA for {item.get('id', 'unknown')}."
            )
