import time

from discord.ext import commands
from modules.emoji import EMOJIS


class PingModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def ping(self, ctx):

        start_time = time.perf_counter()

        latency = round(self.bot.latency * 1000)

        message = await ctx.send(
            f"Pong I think, let me see {EMOJIS['hm']}\n"
            f"Gateway Ping: `{latency}ms`\n"
            f"Calculating round trip, hold on..."
        )

        round_trip = round(
            (time.perf_counter() - start_time) * 1000
        )

        await message.edit(
            content=(
                f"Pong I think, let me see {EMOJIS['hm']}\n"
                f"Gateway Ping: `{latency}ms`\n"
                f"Response Speed: `{round_trip}ms`"
            )
        )


async def setup(bot):
    await bot.add_cog(PingModule(bot))