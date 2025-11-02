"""Command-line entrypoint to start the AI server.

Usage:
  workano-ai-server [--host HOST] [--port PORT] [--openai-key KEY] [--log-level LEVEL]

This will import and run workano_ai_agent_plugin.ai_server.main().
"""
import argparse
import asyncio
import logging
import os
from . import ai_server


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog="workano-ai-server", description="Start the Workano AI realtime server")
    parser.add_argument("--host", default="0.0.0.0", help="UDP listen host (overrides ai_server.UDP_IP)")
    parser.add_argument("--port", type=int, default=4000, help="UDP listen port (overrides ai_server.UDP_PORT)")
    parser.add_argument("--openai-key", default=None, help="OpenAI API key (will set OPENAI_API_KEY env var)")
    parser.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # configure logging
    numeric_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.basicConfig(level=numeric_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # allow overriding constants from ai_server
    ai_server.UDP_IP = args.host
    ai_server.UDP_PORT = args.port

    if args.openai_key:
        os.environ["OPENAI_API_KEY"] = args.openai_key
        # update module-level constant if already read
        ai_server.OPENAI_KEY = args.openai_key

    logger = logging.getLogger("workano.cli")
    logger.info("Starting workano AI server (host=%s port=%d)", args.host, args.port)

    try:
        asyncio.run(ai_server.main())
    except KeyboardInterrupt:
        logger.info("Interrupted, exiting")
    except Exception:
        logger.exception("Unhandled exception in CLI runner")


if __name__ == "__main__":
    main()
