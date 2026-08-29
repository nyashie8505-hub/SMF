import discord
from discord.ext import commands
from modules.general.emoji import EMOJIS

from database import get_connection
from permissions import permission_admin


class UnsignModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # UNSIGN
    # ========================================================

    @commands.command()
    @permission_admin()
    async def unsign(
        self,
        ctx,
        role: discord.Role,
        command_name: str
    ):

        # ====================================================
        # ROLE HIERARCHY
        # ====================================================

        if not ctx.guild:
            return

        is_server_owner = (
            ctx.author.id == ctx.guild.owner_id
        )

        if not is_server_owner:

            if role >= ctx.author.top_role:

                await ctx.send(
                    "{EMOJIS['highlight']} {EMOJIS['false']} You can only manage roles "
                    "below your highest role."
                )

                return

        # ====================================================
        # NORMALIZE COMMAND NAME
        # ====================================================

        command_name = command_name.lower().strip()

        # Remove "du" prefix.

        if command_name != "all":

            if command_name.startswith("du"):

                command_name = command_name[2:]

        # ====================================================
        # EMPTY COMMAND CHECK
        # ====================================================

        if not command_name:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} You must specify a command."
            )

            return

        # ====================================================
        # DUSIGNOWNER CANNOT BE MODIFIED
        # ====================================================

        if command_name == "signowner":

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} `dusignowner` cannot be modified."
            )

            return

        # ====================================================
        # DATABASE
        # ====================================================

        connection = get_connection()
        cursor = connection.cursor()

        # ====================================================
        # DELETE PERMISSION
        # ====================================================

        cursor.execute(
            """
            DELETE FROM command_permissions
            WHERE guild_id = ?
            AND role_id = ?
            AND command_name = ?
            """,
            (
                ctx.guild.id,
                role.id,
                command_name
            )
        )

        deleted = cursor.rowcount

        connection.commit()
        connection.close()

        # ====================================================
        # NOT FOUND
        # ====================================================

        if deleted == 0:

            await ctx.send(
                f"{EMOJIS['highlight']} {EMOJIS['false']} {role.mention} is not signed "
                f"for `{command_name}`."
            )

            return

        # ====================================================
        # SUCCESS
        # ====================================================

        if command_name == "all":

            await ctx.send(
                f"{EMOJIS['highlight']} {EMOJIS['true']} Removed all signed permissions "
                f"from {role.mention}."
            )

        else:

            await ctx.send(
                f"{EMOJIS['highlight']} {EMOJIS['true']} {role.mention} can no longer use "
                f"`du{command_name}`."
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        UnsignModule(bot)
    )