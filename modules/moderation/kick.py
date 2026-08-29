import discord
from discord.ext import commands
from modules.general.emoji import EMOJIS

from permissions import signed_permission


class KickModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @signed_permission()
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason provided"
    ):

        # ========================================================
        # PREVENT SELF KICK
        # ========================================================

        if member == ctx.author:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} You cannot kick yourself."
            )

            return

        # ========================================================
        # PREVENT SERVER OWNER KICK
        # ========================================================

        if member == ctx.guild.owner:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} You cannot kick the server owner."
            )

            return

        # ========================================================
        # MODERATOR ROLE HIERARCHY
        # ========================================================

        if (
            ctx.author != ctx.guild.owner
            and member.top_role >= ctx.author.top_role
        ):

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} You cannot kick a member "
                "with an equal or higher role."
            )

            return

        # ========================================================
        # BOT ROLE HIERARCHY
        # ========================================================

        if member.top_role >= ctx.guild.me.top_role:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} My role is not high enough "
                "to kick this member."
            )

            return

        # ========================================================
        # KICK
        # ========================================================

        try:

            await member.kick(
                reason=(
                    f"{reason} | "
                    f"Kicked by {ctx.author}"
                )
            )

        except discord.Forbidden:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} I do not have permission "
                "to kick this member."
            )

            return

        except discord.HTTPException:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} An error occurred while trying "
                "to kick this member."
            )

            return

        # ========================================================
        # MODLOG
        # ========================================================

        logger = self.bot.get_cog("ModLogModule")

        if logger:

            await logger.log_action(
                guild=ctx.guild,
                action="kick",
                target=member,
                moderator=ctx.author,
                reason=reason
            )

        # ========================================================
        # CONFIRMATION
        # ========================================================

        await ctx.send(
            f"{EMOJIS['highlight']} 👢 {member.mention} has been kicked.\n"
            f"{EMOJIS['highlight']} 📝 Reason: {reason}"
        )


async def setup(bot):

    await bot.add_cog(
        KickModule(bot)
    )