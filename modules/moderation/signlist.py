import discord
from discord.ext import commands

from database import get_connection
from permissions import permission_admin


class SignListModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # SIGN LIST
    # ========================================================

    @commands.command()
    @permission_admin()
    async def signlist(
        self,
        ctx,
        role: discord.Role
    ):

        # ====================================================
        # ROLE HIERARCHY
        # ====================================================
        #
        # Server Owner:
        #   Can view any role.
        #
        # Permission Administrator / Owner Role:
        #   Can view roles below OR equal to their top role.
        #
        # Higher roles:
        #   Cannot view.
        #

        if not ctx.guild:
            return

        is_server_owner = (
            ctx.author.id == ctx.guild.owner_id
        )

        if not is_server_owner:

            if role > ctx.author.top_role:

                await ctx.send(
                    "🔻 ❌ You can only view permissions "
                    "of roles at or below your highest role."
                )

                return

        # ====================================================
        # DATABASE
        # ====================================================

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT command_name
            FROM command_permissions
            WHERE guild_id = ?
            AND role_id = ?
            ORDER BY command_name ASC
            """,
            (
                ctx.guild.id,
                role.id
            )
        )

        permissions = cursor.fetchall()

        connection.close()

        # ====================================================
        # NO PERMISSIONS
        # ====================================================

        if not permissions:

            await ctx.send(
                f"🔻 📋 {role.mention} has no signed commands."
            )

            return

        # ====================================================
        # BUILD COMMAND LIST
        # ====================================================

        command_list = []

        for permission in permissions:

            command_name = permission[0]

            if command_name == "all":

                command_list.append(
                    "🔻 `all` — All signed moderation commands"
                )

            else:

                command_list.append(
                    f"🔻 `du{command_name}`"
                )

        # ====================================================
        # SEND
        # ====================================================

        await ctx.send(
            f"🔻 📋 **Signed commands for "
            f"{role.mention}:**\n\n"
            + "\n".join(command_list)
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        SignListModule(bot)
    )