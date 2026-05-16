"""Executable reproducibility entry point for SoftwareX review."""

from __future__ import annotations

import argparse
import csv
import json
import logging
from pathlib import Path
from typing import Any

import yaml

from core import analyze_results, build_network, evaluate_economics, run_power_flow

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the minimal reproducible distribution-network workflow."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to a YAML configuration file.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where reproducibility artifacts will be written.",
    )
    return parser.parse_args()


def configure_logging() -> None:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "run.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)
    root.addHandler(console_handler)
    root.addHandler(file_handler)


def load_config(path: Path) -> dict[str, Any]:
    logger.info("Loading configuration from %s", path)
    with path.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict):
        raise ValueError(f"Configuration must be a YAML mapping: {path}")
    return config


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write("\n")


def write_voltage_csv(path: Path, voltage_profile: dict[str, float]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["bus_id", "voltage_pu"])
        for bus_id, voltage in voltage_profile.items():
            writer.writerow([bus_id, voltage])


def write_outputs(
    output_dir: Path,
    network: Any,
    simulation_results: dict[str, Any],
    analysis_results: dict[str, Any],
    economics_results: dict[str, Any],
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    artifacts = {
        "network_model": output_dir / "network_model.json",
        "simulation_results": output_dir / "simulation_results.json",
        "analysis_summary": output_dir / "analysis_summary.json",
        "economics_summary": output_dir / "economics_summary.json",
        "voltage_profile": output_dir / "voltage_profile.csv",
        "run_manifest": output_dir / "run_manifest.json",
    }

    write_json(artifacts["network_model"], network.to_dict())
    write_json(artifacts["simulation_results"], simulation_results)
    write_json(artifacts["analysis_summary"], analysis_results)
    write_json(artifacts["economics_summary"], economics_results)
    write_voltage_csv(
        artifacts["voltage_profile"],
        simulation_results["voltage_profile_pu"],
    )

    manifest = {
        key: str(path.as_posix())
        for key, path in artifacts.items()
        if key != "run_manifest"
    }
    write_json(artifacts["run_manifest"], manifest)
    return manifest


def main() -> int:
    args = parse_args()
    configure_logging()

    config_path = Path(args.config)
    output_dir = Path(args.output_dir)

    logger.info("Starting executable reproducibility workflow.")
    config = load_config(config_path)
    network = build_network(config)
    simulation_results = run_power_flow(network, config)
    analysis_results = analyze_results(network, simulation_results, config)
    economics_results = evaluate_economics(
        network,
        simulation_results,
        analysis_results,
        config,
    )
    manifest = write_outputs(
        output_dir,
        network,
        simulation_results,
        analysis_results,
        economics_results,
    )

    logger.info("Reproducible run complete. Artifact manifest: %s", manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
