import time

from discord.ext import commands

from modules.general.emoji import EMOJIS
from database import get_connection


class PingModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def ping(self, ctx):

        # ====================================================
        # START
        # ====================================================

        start_time = time.perf_counter()


        # ====================================================
        # GATEWAY PING
        # ====================================================

        gateway_ping = round(
            self.bot.latency * 1000
        )


        # ====================================================
        # GENERAL PING
        # Time required for Discord command message
        # ====================================================

        general_start = time.perf_counter()

        message = await ctx.send(
            f"# {EMOJIS['highlight']} Pong I think, "
            f"let me see {EMOJIS['hm']}\n"
            f"\n"
            f"{EMOJIS['highlight']} General Ping: `...`\n"
            f"\n"
            f"Gateway Ping: `{gateway_ping}ms`\n"
            f"Database Ping: `...`\n"
            f"Response Speed: `...`"
        )

        general_ping = round(
            (time.perf_counter() - general_start) * 1000
        )


        # ====================================================
        # DATABASE PING
        # ====================================================

        database_start = time.perf_counter()

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT 1"
            )

            cursor.fetchone()

            cursor.close()
            connection.close()

            database_ping = round(
                (time.perf_counter() - database_start) * 1000
            )

            database_status = f"`{database_ping}ms`"

        except Exception:

            database_status = "`ERROR`"


        # ====================================================
        # TOTAL RESPONSE SPEED
        # ====================================================

        response_speed = round(
            (time.perf_counter() - start_time) * 1000
        )


        # ====================================================
        # FINAL
        # ====================================================

        await message.edit(
            content=(
                f"# {EMOJIS['highlight']} Pong I think, "
                f"let me see {EMOJIS['hm']}\n"
                f"\n"
                f"{EMOJIS['highlight']} General Ping: "
                f"`{general_ping}ms`\n"
                f"\n"
                f"Gateway Ping: `{gateway_ping}ms`\n"
                f"Database Ping: {database_status}\n"
                f"Response Speed: `{response_speed}ms`"
            )
        )


async def setup(bot):

    await bot.add_cog(
        PingModule(bot)
    )