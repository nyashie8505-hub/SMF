from discord.ext import commands

from database import get_connection, get_owner_role
from owner_permissions import OWNER_ROLE_COMMANDS


# ============================================================
# COMMAND NAME
# ============================================================

def normalize_command_name(command_name):

    command_name = command_name.lower().strip()

    if command_name.startswith("du"):
        command_name = command_name[2:]

    return command_name


# ============================================================
# SERVER OWNER
# ============================================================

def is_server_owner(ctx):

    if not ctx.guild:
        return False

    return ctx.author.id == ctx.guild.owner_id


# ============================================================
# OWNER ROLE
# ============================================================

def has_owner_role(ctx):

    if not ctx.guild:
        return False

    owner_role_id = get_owner_role(
        ctx.guild.id
    )

    if owner_role_id is None:
        return False

    return any(
        role.id == owner_role_id
        for role in ctx.author.roles
    )


# ============================================================
# OWNER ROLE PERMISSION
# ============================================================

def owner_role_can_use(command_name):

    command_name = normalize_command_name(
        command_name
    )

    # --------------------------------------------------------
    # dusignowner is ALWAYS Server Owner only.
    # --------------------------------------------------------

    if command_name == "signowner":
        return False

    # --------------------------------------------------------
    # "all" = all commands except dusignowner.
    # --------------------------------------------------------

    if "all" in OWNER_ROLE_COMMANDS:
        return True

    # --------------------------------------------------------
    # Specific command
    # --------------------------------------------------------

    return command_name in {
        normalize_command_name(name)
        for name in OWNER_ROLE_COMMANDS
    }


# ============================================================
# SIGNED ROLE PERMISSION
# ============================================================

def signed_role_can_use(ctx, command_name):

    if not ctx.guild:
        return False

    command_name = normalize_command_name(
        command_name
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT role_id, command_name

        FROM command_permissions

        WHERE guild_id = ?
        AND (
            command_name = ?
            OR command_name = 'all'
        )
        """,
        (
            ctx.guild.id,
            command_name
        )
    )

    permissions = cursor.fetchall()

    connection.close()

    user_role_ids = {
        role.id
        for role in ctx.author.roles
    }

    for role_id, permission in permissions:

        if role_id in user_role_ids:
            return True

    return False


# ============================================================
# PERMISSION ADMIN
# ============================================================

def has_permission_admin(ctx):
    """
    Permission administrator.

    Allowed:
    - Server Owner
    - Owner Role
    - Discord Administrator

    NOT allowed:
    - Normal signed roles
    """

    if not ctx.guild:
        return False

    # --------------------------------------------------------
    # Server Owner
    # --------------------------------------------------------

    if is_server_owner(ctx):
        return True

    # --------------------------------------------------------
    # Owner Role
    # --------------------------------------------------------

    if has_owner_role(ctx):
        return True

    # --------------------------------------------------------
    # Discord Administrator
    # --------------------------------------------------------

    if ctx.author.guild_permissions.administrator:
        return True

    return False


# ============================================================
# PERMISSION ADMIN DECORATOR
# ============================================================

def permission_admin():

    async def predicate(ctx):

        allowed = has_permission_admin(ctx)

        if not allowed:

            await ctx.send(
                "🔻 ❌ You do not have permission "
                "to manage command permissions."
            )

        return allowed

    return commands.check(predicate)


# ============================================================
# MAIN PERMISSION CHECK
# ============================================================

async def has_command_permission(ctx):

    if not ctx.guild:
        return False

    command_name = normalize_command_name(
        ctx.command.name
    )

    # ========================================================
    # DUSIGNOWNER
    # ========================================================
    #
    # ONLY SERVER OWNER.
    #
    # Administrator: NO
    # Owner Role: NO
    # Signed Role: NO
    #

    if command_name == "signowner":

        return is_server_owner(ctx)

    # ========================================================
    # SERVER OWNER
    # ========================================================

    if is_server_owner(ctx):

        return True

    # ========================================================
    # OWNER ROLE
    # ========================================================

    if has_owner_role(ctx):

        return owner_role_can_use(
            command_name
        )

    # ========================================================
    # ADMINISTRATOR
    # ========================================================
    #
    # Administrator can use normal commands.
    #
    # dusignowner was already handled above.
    #

    if ctx.author.guild_permissions.administrator:

        return True

    # ========================================================
    # SIGNED ROLES
    # ========================================================

    if signed_role_can_use(
        ctx,
        command_name
    ):

        return True

    # ========================================================
    # DENIED
    # ========================================================

    return False


# ============================================================
# SIGNED PERMISSION DECORATOR
# ============================================================

def signed_permission():

    async def predicate(ctx):

        allowed = await has_command_permission(
            ctx
        )

        if not allowed:

            await ctx.send(
                "🔻 ❌ You do not have permission "
                "to use this command."
            )

        return allowed

    return commands.check(predicate)