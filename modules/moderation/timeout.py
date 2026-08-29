import re
import discord

from datetime import timedelta
from discord.ext import commands

from permissions import signed_permission


def parse_time(value: str):

    value = value.lower().strip()

    match = re.fullmatch(
        r"(\d+)\s*(m|minute|minutes)",
        value
    )

    if not match:
        return None

    minutes = int(
        match.group(1)
    )

    if minutes <= 0:
        return None

    return timedelta(
        minutes=minutes
    )


class TimeoutModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @signed_permission()
    @commands.bot_has_permissions(
        moderate_members=True
    )
    async def timeout(
        self,
        ctx,
        member: discord.Member,
        duration: str,
        *,
        reason="No reason provided"
    ):

        # ========================================================
        # PARSE TIME
        # ========================================================

        timeout_duration = parse_time(
            duration
        )

        if timeout_duration is None:

            await ctx.send(
                "🔻 ❌ Invalid time format.\n"
                "🔻 📌 Examples: `1m`, `2m`, "
                "`1minute`, `2minutes`"
            )

            return

        # ========================================================
        # PREVENT SELF TIMEOUT
        # ========================================================

        if member == ctx.author:

            await ctx.send(
                "🔻 ❌ You cannot timeout yourself."
            )

            return

        # ========================================================
        # SERVER OWNER
        # ========================================================

        if member == ctx.guild.owner:

            await ctx.send(
                "🔻 ❌ You cannot timeout the server owner."
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
                "🔻 ❌ You cannot timeout a member "
                "with an equal or higher role."
            )

            return

        # ========================================================
        # BOT ROLE HIERARCHY
        # ========================================================

        if member.top_role >= ctx.guild.me.top_role:

            await ctx.send(
                "🔻 ❌ My role is not high enough "
                "to timeout this member."
            )

            return

        # ========================================================
        # TIMEOUT UNTIL
        # ========================================================

        timeout_until = (
            discord.utils.utcnow()
            + timeout_duration
        )

        minutes = int(
            timeout_duration.total_seconds() / 60
        )

        # ========================================================
        # APPLY TIMEOUT
        # ========================================================

        try:

            await member.edit(
                timed_out_until=timeout_until,
                reason=(
                    f"{reason} | "
                    f"Moderated by {ctx.author}"
                )
            )

        except discord.Forbidden:

            await ctx.send(
                "🔻 ❌ I do not have permission "
                "to timeout this member."
            )

            return

        except discord.HTTPException:

            await ctx.send(
                "🔻 ❌ An error occurred while trying "
                "to timeout this member."
            )

            return

        # ========================================================
        # MODLOG
        # ========================================================

        logger = self.bot.get_cog("ModLogModule")

        if logger:

            await logger.log_action(
                guild=ctx.guild,
                action="timeout",
                target=member,
                moderator=ctx.author,
                reason=reason,
                details=(
                    f"Duration: `{minutes} minute(s)`\n"
                    f"Until: <t:{int(timeout_until.timestamp())}:F>"
                )
            )

        # ========================================================
        # CONFIRMATION
        # ========================================================

        await ctx.send(
            f"🔻 ✅ {member.mention} has been timed out.\n"
            f"🔻 ⏱️ Duration: `{minutes} minute(s)`\n"
            f"🔻 📝 Reason: {reason}"
        )


async def setup(bot):

    await bot.add_cog(
        TimeoutModule(bot)
    )