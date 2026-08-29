from permissions import signed_permission
import discord
from discord.ext import commands

from database import get_connection


class WarnListModule(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    @commands.command()
    @signed_permission()
    async def warnlist(
        self,
        ctx,
        member: discord.Member
    ):

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                moderator_id,
                reason,
                created_at

            FROM warnings

            WHERE guild_id = ?
            AND user_id = ?

            ORDER BY id DESC
            """,
            (
                ctx.guild.id,
                member.id
            )
        )

        warnings = cursor.fetchall()

        connection.close()


        if not warnings:

            await ctx.send(
                f"🔻 📋 {member.mention} has no warnings."
            )

            return


        content = (
            f"🔻 📋 **Warnings for {member}**\n\n"
        )


        for warning in warnings:

            warning_id = warning[0]
            moderator_id = warning[1]
            reason = warning[2]
            created_at = warning[3]


            content += (
                f"🔻 ⚠️ Warning ID: `{warning_id}`\n"
                f"🔻 📝 Reason: {reason}\n"
                f"🔻 👤 Moderator: <@{moderator_id}>\n"
                f"🔻 ⏱️ Issued: <t:{created_at}:R>\n\n"
            )


        # Prevent exceeding Discord's message limit
        if len(content) > 1900:

            content = (
                content[:1900]
                + "\n🔻 ⚠️ List truncated."
            )


        await ctx.send(content)


async def setup(bot):

    await bot.add_cog(
        WarnListModule(bot)
    )