"""
FFile: cli.py
Author: MORS
Date: 20 Dec 25

Description:
Provides a command-line interface for the application.
Responsible solely for parsing and validating user-supplied arguments.
Does not perform routing, ingestion, analysis, or formatting.

Responsibilities:
  - Define command-line arguments using argparse.
  - Validate and return parsed arguments to the caller.
  - Support optional model selection, config file path, and verbose mode.

Not Responsible For:
  - Executing commands or routing logic.
  - Managing conversations or models.
  - Loading files, ingesting data, or performing analysis.
  - Any GUI or REPL behavior.

Public API Contract:

  Functions:
    - parse_args()
        Inputs: none
        Outputs: argparse.Namespace
        Notes: Returns parsed CLI arguments for use by main.py or other callers.

Static Methods:
  - None
"""

import argparse


# Parses command-line arguments - Returns: argparse.Namespace: Parsed arguments containing user-specified options
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI agent locally using Ollama and downloaded models.")

    parser.add_argument(
        "--model",
        type=str,
        help="Model being used.",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Optional path to a configuration file.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging or detailed logs.",
    )

    return parser.parse_args()
