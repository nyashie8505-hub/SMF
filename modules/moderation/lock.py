from permissions import signed_permission
import discord
from discord.ext import commands
from modules.general.emoji import EMOJIS


class LockModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @signed_permission()
    @commands.bot_has_permissions(
        manage_channels=True
    )
    async def lock(
        self,
        ctx
    ):

        overwrite = ctx.channel.overwrites_for(
            ctx.guild.default_role
        )

        overwrite.send_messages = False


        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            overwrite=overwrite,
            reason=(
                f"Channel locked by {ctx.author}"
            )
        )


        await ctx.send(
            "{EMOJIS['highlight']} 🔒 This channel has been locked."
        )


async def setup(bot):

    await bot.add_cog(
        LockModule(bot)
    )