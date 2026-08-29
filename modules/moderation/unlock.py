from permissions import signed_permission
import discord
from discord.ext import commands


class UnlockModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @signed_permission()
    @commands.bot_has_permissions(
        manage_channels=True
    )
    async def unlock(
        self,
        ctx
    ):

        overwrite = ctx.channel.overwrites_for(
            ctx.guild.default_role
        )

        overwrite.send_messages = None


        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            overwrite=overwrite,
            reason=(
                f"Channel unlocked by {ctx.author}"
            )
        )


        await ctx.send(
            "🔻 🔓 This channel has been unlocked."
        )


async def setup(bot):

    await bot.add_cog(
        UnlockModule(bot)
    )