import os
import sys
import json
import asyncio
import pathlib

import discord
from discord.ext import commands

from bot import db
from bot.errors import CommandDisabledError

TESTING_GUILDS: list[int] | None = (
    list(map(int, json.loads(os.environ.get("TESTING_GUILDS") or "[]")))
    if "--debug" in sys.argv
    else None
)
bot = commands.Bot(description="Eggs Benedict")


@bot.event
async def on_ready():
    if user := bot.user:
        print("Logged in as", user)


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, CommandDisabledError):
        await ctx.respond(
            f"`/{error.command.qualified_name}` is disabled in this server. If you believe this is a mistake please contact a server admin or my developers.",
            ephemeral=True,
        )
        return

    await ctx.respond(
        f"Something went wrong while cooking your Eggs Benedict, please copy paste the following text and report it to my developers:```{error}```",
        ephemeral=True,
    )
    raise error


@bot.slash_command(guild_ids=TESTING_GUILDS)
async def ping(ctx: discord.ApplicationContext):
    """
    Get the bot's websocket latency. You don't have to worry about this unless the bot is lagging.
    """

    latency = ctx.bot.latency * 1000
    await ctx.respond(f"Pong! Latency is {latency:.2f} ms")


def load_cogs():
    cogs_dir = pathlib.Path(__file__).parent / "cogs"

    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            bot.load_extension(f"bot.cogs.{module_name}")
            print(f"Loaded {module_name} cog")


def main(token: str):
    loop = asyncio.get_event_loop()
    load_cogs()

    try:
        db.init_engine()
        loop.run_until_complete(bot.start(token))
    except KeyboardInterrupt or SystemExit:
        pass
    finally:
        print("Exiting...")
        loop.run_until_complete(bot.close())
        loop.run_until_complete(db.close())
