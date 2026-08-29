import discord

from discord.ext import commands

from modules.general.emoji import EMOJIS

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
        # SERVER CHECK
        # ====================================================

        if not ctx.guild:
            return


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

        is_server_owner = (
            ctx.author.id == ctx.guild.owner_id
        )

        if not is_server_owner:

            if role >= ctx.author.top_role:

                await ctx.send(
                    f"{EMOJIS['highlight']} "
                    f"{EMOJIS['false']} "
                    f"You can only manage roles "
                    f"below your highest role."
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
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                f"You must specify a command."
            )

            return


        # ====================================================
        # DUSIGNOWNER CANNOT BE SIGNED
        # ====================================================

        if command_name == "signowner":

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                f"`dusignowner` can only be used "
                f"by the server owner."
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
                    f"{EMOJIS['highlight']} "
                    f"{EMOJIS['false']} "
                    f"That command does not exist."
                )

                return


        # ====================================================
        # DATABASE
        # ====================================================

        connection = get_connection()
        cursor = connection.cursor()


        try:

            # ====================================================
            # CHECK EXISTING PERMISSION
            # ====================================================

            cursor.execute(
                """
                SELECT 1
                FROM command_permissions
                WHERE guild_id = %s
                AND role_id = %s
                AND command_name = %s
                """,
                (
                    ctx.guild.id,
                    role.id,
                    command_name
                )
            )

            existing = cursor.fetchone()


            if existing is not None:

                return_message = (
                    f"{EMOJIS['highlight']} "
                    f"{EMOJIS['false']} "
                    f"{role.mention} is already signed "
                    f"for `{command_name}`."
                )

            else:

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
                    VALUES (%s, %s, %s)
                    """,
                    (
                        ctx.guild.id,
                        role.id,
                        command_name
                    )
                )

                connection.commit()


                # ====================================================
                # SUCCESS
                # ====================================================

                if command_name == "all":

                    return_message = (
                        f"{EMOJIS['highlight']} "
                        f"{EMOJIS['true']} "
                        f"{role.mention} can now use "
                        f"all signed moderation commands."
                    )

                else:

                    return_message = (
                        f"{EMOJIS['highlight']} "
                        f"{EMOJIS['true']} "
                        f"{role.mention} can now use "
                        f"`du{command_name}`."
                    )


        finally:

            cursor.close()
            connection.close()


        await ctx.send(
            return_message
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        SignModule(bot)
    )