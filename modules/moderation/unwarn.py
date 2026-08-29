import os
import sqlite3
import discord
from modules.general.emoji import EMOJIS

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


class UnwarnModule(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        initialize_database()

    @commands.command()
    @signed_permission()
    async def unwarn(
        self,
        ctx,
        warning_id: int
    ):

        # ========================================================
        # GET WARNING
        # ========================================================

        connection = sqlite3.connect(
            DATABASE
        )

        connection.row_factory = sqlite3.Row

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    user_id,
                    moderator_id,
                    reason,
                    created_at
                FROM warnings
                WHERE id = ?
                AND guild_id = ?
                """,
                (
                    warning_id,
                    ctx.guild.id
                )
            )

            warning = cursor.fetchone()

            if warning is None:

                await ctx.send(
                    "{EMOJIS['highlight']} {EMOJIS['false']} Warning not found."
                )

                return

            # ====================================================
            # DELETE WARNING
            # ====================================================

            cursor.execute(
                """
                DELETE FROM warnings
                WHERE id = ?
                AND guild_id = ?
                """,
                (
                    warning_id,
                    ctx.guild.id
                )
            )

            connection.commit()

        finally:

            connection.close()

        # ========================================================
        # FIND MEMBER
        # ========================================================

        member = ctx.guild.get_member(
            warning["user_id"]
        )

        # ========================================================
        # MODLOG
        # ========================================================

        logger = self.bot.get_cog(
            "ModLogModule"
        )

        if logger:

            await logger.log_action(
                guild=ctx.guild,
                action="unwarn",
                target=member,
                moderator=ctx.author,
                details=(
                    f"Warning ID: `{warning_id}`\n"
                    f"Original reason: {warning['reason']}"
                )
            )

        # ========================================================
        # CONFIRMATION
        # ========================================================

        await ctx.send(
            f"{EMOJIS['highlight']} {EMOJIS['true']} Warning `{warning_id}` has been removed."
        )


async def setup(bot):

    await bot.add_cog(
        UnwarnModule(bot)
    )