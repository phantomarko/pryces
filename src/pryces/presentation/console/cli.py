"""CLI entry point for console commands.

This module provides command-line interface functionality for the application.
It can be run directly or integrated into setup.py console_scripts.
"""

import argparse
import logging
import sys

from ...infrastructure.providers import YahooFinanceProvider
from .commands.factories import CommandFactory
from .menu import InteractiveMenu


def configure_logging(verbose: bool = False) -> None:
    """Configure logging for CLI execution.

    Logs are sent to stderr to keep stdout clean for JSON output.
    """
    log_level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )




def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description='Stock price information system - Interactive Menu',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging to stderr'
    )

    args = parser.parse_args()

    configure_logging(args.verbose)

    try:
        provider = YahooFinanceProvider()
        factory = CommandFactory(stock_price_provider=provider)

        registry = factory.create_command_registry()
        menu = InteractiveMenu(registry)
        menu.run()
        return 0

    except Exception as e:
        logging.error(f"CLI error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
