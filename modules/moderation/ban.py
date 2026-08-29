import discord
from discord.ext import commands
from modules.general.emoji import EMOJIS

from permissions import signed_permission


class BanModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @signed_permission()
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason provided"
    ):

        # ========================================================
        # PREVENT SELF BAN
        # ========================================================

        if member == ctx.author:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} What are you doing? You can't ban yourself, bro."
            )

            return

        # ========================================================
        # PREVENT SERVER OWNER BAN
        # ========================================================

        if member == ctx.guild.owner:

            await ctx.send(
                "{EMOJIS['highlight']} ❌{EMOJIS['false']} You cannot ban the server owner."
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
                "{EMOJIS['highlight']} {EMOJIS['false']} You cannot ban a member with an equal or higher role."
            )

            return

        # ========================================================
        # BOT ROLE HIERARCHY
        # ========================================================

        if member.top_role >= ctx.guild.me.top_role:

            await ctx.send(
                f"{EMOJIS['highlight']} {EMOJIS['false']} My role is not high enough to ban this member."
            )

            return

        # ========================================================
        # BAN
        # ========================================================

        try:

            await member.ban(
                reason=(
                    f"{reason} | "
                    f"Banned by {ctx.author}"
                )
            )

        except discord.Forbidden:

            await ctx.send(
                f"{EMOJIS['highlight']} {EMOJIS['false']} I do not have permission to ban this member."
            )

            return

        except discord.HTTPException:

            await ctx.send(
                f"{EMOJIS['highlight']} {EMOJIS['false']} **{member.mention}** could not be banned.\n"
                f"An error occurred while trying to ban this member."
            )

            return

        # ========================================================
        # MODLOG
        # ========================================================

        logger = self.bot.get_cog("ModLogModule")

        if logger:

            await logger.log_action(
                guild=ctx.guild,
                action="ban",
                target=member,
                moderator=ctx.author,
                reason=reason
            )

        # ========================================================
        # CONFIRMATION
        # ========================================================

        await ctx.send(
            f"{EMOJIS['highlight']} {EMOJIS['banned']} **{member.mention}** has been banned.\n"
            f"{EMOJIS['highlight']} 📝 Reason: {reason}"
        )


async def setup(bot):

    await bot.add_cog(
        BanModule(bot)
    )