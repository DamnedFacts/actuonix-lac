"""CLI entrypoints"""
from typing import Any
import asyncio
import logging

import click
from actuonix_lac.aio import AsyncLAC


LOGGER = logging.getLogger(__name__)


@click.group()
@click.option("-l", "--loglevel", help="Python log level, 10=DEBUG, 20=INFO, 30=WARNING, 40=CRITICAL", default=30)
@click.option("-v", "--verbose", count=True, help="Shorthand for info/debug loglevel (-v/-vv)")
@click.pass_context
def commonopts(ctx: Any, loglevel: int, verbose: int) -> None:
    """CLI wrapper for select methods in AsyncLAC"""
    if verbose == 1:
        loglevel = 20
    if verbose >= 2:
        loglevel = 10
    logging.getLogger("").setLevel(loglevel)
    LOGGER.setLevel(loglevel)
    ctx.ensure_object(dict)
    ctx.obj["servo"] = AsyncLAC()
    ctx.obj["loop"] = asyncio.get_event_loop()


@commonopts.command()
@click.argument("value", type=int)
@click.pass_context
def set_position(ctx: Any, value: int) -> None:
    """Set the raw position, between 0-1023"""
    ctx.obj["loop"].run_until_complete(ctx.obj["servo"].set_position(value))


@commonopts.command()
@click.pass_context
def get_position(ctx: Any) -> None:
    """Get the raw actual position, between 0-1023"""
    pos = ctx.obj["loop"].run_until_complete(ctx.obj["servo"].get_feedback())
    click.echo(pos)


def laccontrol() -> None:
    """CLI entrypoint"""
    commonopts()  # pylint: disable=E1120
