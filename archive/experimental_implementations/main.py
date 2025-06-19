#!/usr/bin/env python3
"""Main entry point for Super-Digimon MCP server."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.mcp_server import run_server
from src.utils.config import Config


def setup_logging(config: Config):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('super_digimon.log')
        ]
    )


def main():
    """Main entry point."""
    # Load configuration
    config = Config()
    config.ensure_directories()
    
    # Set up logging
    setup_logging(config)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Super-Digimon MCP server...")
    
    # Run the server
    try:
        asyncio.run(run_server(config))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()