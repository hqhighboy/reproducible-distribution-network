# Reproduction Instructions

This repository provides a minimal executable reproducibility layer for distribution-network studies. The implementation is intentionally lightweight: it preserves the workflow structure, logging, configuration loading, and artifact writing needed by reviewers, while the mathematical optimization and detailed power-flow routines are represented by deterministic placeholder logic.

## Setup

Create a Python environment and install the required dependencies:

```bash
pip install -r requirements.txt
```

## Run the IEEE 33-bus demo

From the repository root, execute:

```bash
python main.py --config configs/ieee33_benchmark.yaml --output-dir outputs/demo
```

The command writes logs to `logs/run.log` and reproducibility artifacts to `outputs/demo`.

## Alternative anonymized engineering feeder

The anonymized 10 kV feeder can be executed with:

```bash
python main.py --config configs/engineering_feeder_anon.yaml --output-dir outputs/demo
```

Transformer capacities in this mock engineering feeder are constrained to standard distribution values between 50 kVA and 630 kVA.
