import discord

from discord.ext import commands

from modules.general.emoji import EMOJIS
from permissions import signed_only_permission


class TupperModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # DUTUP
    # ========================================================

    @commands.command(name="tup")
    @signed_only_permission()
    async def tup(
        self,
        ctx,
        *,
        content: str = None
    ):

        # ====================================================
        # EMPTY MESSAGE
        # ====================================================

        if not content:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                f"You must provide a message."
            )

            return

        # ====================================================
        # DELETE COMMAND MESSAGE
        # ====================================================

        try:

            await ctx.message.delete()

        except discord.Forbidden:
            pass

        except discord.HTTPException:
            pass

        # ====================================================
        # SEND MESSAGE
        # ====================================================

        await ctx.send(
            content
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        TupperModule(bot)
    )