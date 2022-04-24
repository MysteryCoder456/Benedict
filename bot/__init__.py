import os
import sys
import json
import asyncio

import discord
from discord.ext import commands

from bot import db

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


@bot.slash_command(guild_ids=TESTING_GUILDS)
async def ping(ctx: discord.ApplicationContext):
    """
    Get the bot's websocket latency. You don't have to worry about this unless the bot is lagging.
    """

    latency = ctx.bot.latency * 1000
    await ctx.respond(f"Pong! Latency is {latency:.2f} ms")


def main(token: str):
    loop = asyncio.get_event_loop()

    try:
        db.init_engine()
        loop.run_until_complete(bot.start(token))
    except KeyboardInterrupt or SystemExit:
        pass
    finally:
        print("Exiting...")
        loop.run_until_complete(bot.close())
        loop.run_until_complete(db.close())
