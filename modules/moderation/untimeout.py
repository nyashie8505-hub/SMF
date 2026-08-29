import discord
from modules.general.emoji import EMOJIS

from discord.ext import commands

from permissions import signed_permission


class UnTimeoutModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @signed_permission()
    @commands.bot_has_permissions(
        moderate_members=True
    )
    async def untimeout(
        self,
        ctx,
        member: discord.Member
    ):

        # ========================================================
        # PREVENT SELF UNTIMEOUT
        # ========================================================

        if member == ctx.author:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} You cannot remove your own timeout."
            )

            return

        # ========================================================
        # CHECK TIMEOUT
        # ========================================================

        if not member.is_timed_out():

            await ctx.send(
                f"{EMOJIS['highlight']} ⚠️ {member.mention} is not timed out."
            )

            return

        # ========================================================
        # ROLE HIERARCHY
        # ========================================================

        if (
            ctx.author != ctx.guild.owner
            and member.top_role >= ctx.author.top_role
        ):

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} You cannot moderate a member "
                "with an equal or higher role."
            )

            return

        # ========================================================
        # REMOVE TIMEOUT
        # ========================================================

        try:

            await member.edit(
                timed_out_until=None,
                reason=f"Timeout removed by {ctx.author}"
            )

        except discord.Forbidden:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} I do not have permission "
                "to remove this timeout."
            )

            return

        except discord.HTTPException:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} An error occurred while trying "
                "to remove the timeout."
            )

            return

        # ========================================================
        # MODLOG
        # ========================================================

        logger = self.bot.get_cog("ModLogModule")

        if logger:

            await logger.log_action(
                guild=ctx.guild,
                action="untimeout",
                target=member,
                moderator=ctx.author,
                reason="Timeout removed."
            )

        # ========================================================
        # CONFIRMATION
        # ========================================================

        await ctx.send(
            f"{EMOJIS['highlight']} {EMOJIS['true']} Timeout removed from {member.mention}."
        )


async def setup(bot):

    await bot.add_cog(
        UnTimeoutModule(bot)
    )