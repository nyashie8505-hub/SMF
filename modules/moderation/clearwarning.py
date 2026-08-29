import os
import sqlite3
import discord

from discord.ext import commands

from permissions import signed_permission


DATABASE = "data/smf.db"


def initialize_database():

    os.makedirs(
        "data",
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            moderator_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


class ClearWarningModule(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        initialize_database()

    @commands.command()
    @signed_permission()
    async def clearwarning(
        self,
        ctx,
        member: discord.Member
    ):

        # ========================================================
        # PREVENT SELF CLEAR
        # ========================================================

        if member == ctx.author:

            await ctx.send(
                "🔻 ❌ You cannot clear your own warnings."
            )

            return

        # ========================================================
        # DATABASE
        # ========================================================

        connection = sqlite3.connect(
            DATABASE
        )

        try:

            cursor = connection.cursor()

            # ====================================================
            # COUNT WARNINGS
            # ====================================================

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM warnings
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    ctx.guild.id,
                    member.id
                )
            )

            warning_count = cursor.fetchone()[0]

            if warning_count == 0:

                await ctx.send(
                    f"🔻 ❌ {member.mention} has no warnings."
                )

                return

            # ====================================================
            # DELETE WARNINGS
            # ====================================================

            cursor.execute(
                """
                DELETE FROM warnings
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    ctx.guild.id,
                    member.id
                )
            )

            connection.commit()

        finally:

            connection.close()

        # ========================================================
        # MODLOG
        # ========================================================

        logger = self.bot.get_cog(
            "ModLogModule"
        )

        if logger:

            await logger.log_action(
                guild=ctx.guild,
                action="clearwarning",
                target=member,
                moderator=ctx.author,
                details=(
                    f"Warnings cleared: `{warning_count}`"
                )
            )

        # ========================================================
        # CONFIRMATION
        # ========================================================

        await ctx.send(
            f"🔻 ✅ Cleared `{warning_count}` warning(s) "
            f"from {member.mention}."
        )


async def setup(bot):

    await bot.add_cog(
        ClearWarningModule(bot)
    )