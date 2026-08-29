import discord
from discord.ext import commands

from database import get_connection
from permissions import permission_admin


class SignModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # SIGN
    # ========================================================

    @commands.command()
    @permission_admin()
    async def sign(
        self,
        ctx,
        role: discord.Role,
        command_name: str
    ):

        # ====================================================
        # ROLE HIERARCHY
        # ====================================================
        #
        # Server Owner:
        #   Can manage any role.
        #
        # Everyone else with permission_admin:
        #   Can only manage roles BELOW their highest role.
        #

        if not ctx.guild:
            return

        is_server_owner = (
            ctx.author.id == ctx.guild.owner_id
        )

        if not is_server_owner:

            if role >= ctx.author.top_role:

                await ctx.send(
                    "🔻 ❌ You can only manage roles "
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
                "🔻 ❌ You must specify a command."
            )

            return

        # ====================================================
        # DUSIGNOWNER CANNOT BE SIGNED
        # ====================================================

        if command_name == "signowner":

            await ctx.send(
                "🔻 ❌ `dusignowner` can only be used "
                "by the server owner."
            )

            return

        # ====================================================
        # CHECK COMMAND EXISTS
        # ====================================================

        if command_name != "all":

            command = self.bot.get_command(
                command_name
            )

            if command is None:

                await ctx.send(
                    "🔻 ❌ That command does not exist."
                )

                return

        # ====================================================
        # DATABASE
        # ====================================================

        connection = get_connection()
        cursor = connection.cursor()

        # ====================================================
        # CHECK EXISTING PERMISSION
        # ====================================================

        cursor.execute(
            """
            SELECT 1
            FROM command_permissions
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

        existing = cursor.fetchone()

        if existing is not None:

            connection.close()

            await ctx.send(
                f"🔻 ❌ {role.mention} is already "
                f"signed for `{command_name}`."
            )

            return

        # ====================================================
        # ADD PERMISSION
        # ====================================================

        cursor.execute(
            """
            INSERT INTO command_permissions (
                guild_id,
                role_id,
                command_name
            )
            VALUES (?, ?, ?)
            """,
            (
                ctx.guild.id,
                role.id,
                command_name
            )
        )

        connection.commit()
        connection.close()

        # ====================================================
        # SUCCESS
        # ====================================================

        if command_name == "all":

            await ctx.send(
                f"🔻 ✅ {role.mention} can now use "
                "all signed moderation commands."
            )

        else:

            await ctx.send(
                f"🔻 ✅ {role.mention} can now use "
                f"`du{command_name}`."
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        SignModule(bot)
    )