import discord
from discord.ext import commands

from permissions import signed_permission


class UnbanModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @signed_permission()
    @commands.bot_has_permissions(ban_members=True)
    async def unban(
        self,
        ctx,
        user_id: int
    ):

        # ========================================================
        # FETCH USER
        # ========================================================

        try:

            user = await self.bot.fetch_user(
                user_id
            )

        except discord.NotFound:

            await ctx.send(
                "🔻 ❌ User not found."
            )

            return

        except discord.HTTPException:

            await ctx.send(
                "🔻 ❌ Failed to fetch this user."
            )

            return

        # ========================================================
        # CHECK BAN
        # ========================================================

        try:

            ban_entry = await ctx.guild.fetch_ban(
                user
            )

        except discord.NotFound:

            await ctx.send(
                "🔻 ❌ This user is not banned."
            )

            return

        except discord.Forbidden:

            await ctx.send(
                "🔻 ❌ I do not have permission "
                "to view the ban list."
            )

            return

        except discord.HTTPException:

            await ctx.send(
                "🔻 ❌ Failed to check the ban list."
            )

            return

        # ========================================================
        # UNBAN
        # ========================================================

        try:

            await ctx.guild.unban(
                ban_entry.user,
                reason=f"Unbanned by {ctx.author}"
            )

        except discord.Forbidden:

            await ctx.send(
                "🔻 ❌ I do not have permission "
                "to unban users."
            )

            return

        except discord.HTTPException:

            await ctx.send(
                "🔻 ❌ An error occurred while trying "
                "to unban this user."
            )

            return

        # ========================================================
        # MODLOG
        # ========================================================

        logger = self.bot.get_cog("ModLogModule")

        if logger:

            await logger.log_action(
                guild=ctx.guild,
                action="unban",
                target=ban_entry.user,
                moderator=ctx.author,
                reason="User unbanned."
            )

        # ========================================================
        # CONFIRMATION
        # ========================================================

        await ctx.send(
            f"🔻 ✅ {ban_entry.user.mention} has been unbanned."
        )


async def setup(bot):

    await bot.add_cog(
        UnbanModule(bot)
    )