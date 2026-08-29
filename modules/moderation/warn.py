import os
import sqlite3
import discord

from datetime import datetime, timezone
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


class WarnModule(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        initialize_database()

    @commands.command()
    @signed_permission()
    async def warn(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No reason provided"
    ):

        # ========================================================
        # PREVENT SELF WARN
        # ========================================================

        if member == ctx.author:

            await ctx.send(
                "🔻 ❌ You cannot warn yourself."
            )

            return

        # ========================================================
        # SERVER OWNER
        # ========================================================

        if member == ctx.guild.owner:

            await ctx.send(
                "🔻 ❌ You cannot warn the server owner."
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
                "🔻 ❌ You cannot warn a member "
                "with an equal or higher role."
            )

            return

        # ========================================================
        # BOT ROLE HIERARCHY
        # ========================================================

        if member.top_role >= ctx.guild.me.top_role:

            await ctx.send(
                "🔻 ❌ My role is not high enough "
                "to moderate this member."
            )

            return

        # ========================================================
        # TIMESTAMP
        # ========================================================

        created_at = int(
            datetime.now(
                timezone.utc
            ).timestamp()
        )

        # ========================================================
        # INSERT WARNING
        # ========================================================

        connection = sqlite3.connect(
            DATABASE
        )

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO warnings (
                    guild_id,
                    user_id,
                    moderator_id,
                    reason,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    ctx.guild.id,
                    member.id,
                    ctx.author.id,
                    reason,
                    created_at
                )
            )

            warning_id = cursor.lastrowid

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
                action="warn",
                target=member,
                moderator=ctx.author,
                reason=reason,
                details=f"Warning ID: `{warning_id}`"
            )

        # ========================================================
        # CONFIRMATION
        # ========================================================

        await ctx.send(
            f"🔻 ⚠️ {member.mention} has received a warning.\n"
            f"🔻 🆔 Warning ID: `{warning_id}`\n"
            f"🔻 📝 Reason: {reason}\n"
            f"🔻 ⏱️ Issued: <t:{created_at}:R>"
        )


async def setup(bot):

    await bot.add_cog(
        WarnModule(bot)
    )