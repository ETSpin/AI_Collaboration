"""
File: cli.py
Author: MORS
Date: 20 Dec 25

Description:
Provides a command-line interface.
This module is responsible for parsing user-supplied arguments, validating them, and routing execution to
the appropriate subsystems such as ingestion, analysis, or formatting.

Usage:
Imported by main.py or executed indirectly 
"""

import argparse


    # Parses command-line arguments - Returns: argparse.Namespace: Parsed arguments containing user-specified options
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AdvisorAIDesk: AI-assisted stock research and analysis."
    )

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