import discord
from discord.ext import commands

from database import get_owner_role, set_owner_role


class SignOwnerModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def signowner(
        self,
        ctx,
        role: discord.Role
    ):

        # ========================================================
        # GUILD CHECK
        # ========================================================

        if not ctx.guild:
            return


        # ========================================================
        # ONLY SERVER OWNER
        # ========================================================

        if ctx.author.id != ctx.guild.owner_id:

            await ctx.send(
                "🔻 ❌ Only the server owner can use "
                "`dusignowner`."
            )

            return


        # ========================================================
        # ROLE VALIDATION
        # ========================================================

        # Cannot use @everyone
        if role.is_default():

            await ctx.send(
                "🔻 ❌ You cannot use @everyone "
                "as the Owner Role."
            )

            return


        # Cannot use managed/integration roles
        if role.managed:

            await ctx.send(
                "🔻 ❌ You cannot use a managed/integration "
                "role as the Owner Role."
            )

            return


        # ========================================================
        # NO ROLE HIERARCHY CHECK
        # ========================================================
        #
        # Server Owner can select ANY normal role.
        #
        # Do NOT check:
        #
        #     role >= ctx.author.top_role
        #
        # because the server owner is above the normal
        # role hierarchy for permission purposes.
        #


        # ========================================================
        # CURRENT OWNER ROLE
        # ========================================================

        current_role_id = get_owner_role(
            ctx.guild.id
        )


        # Already the Owner Role
        if current_role_id == role.id:

            await ctx.send(
                f"🔻 ❌ {role.mention} is already "
                "the Owner Role."
            )

            return


        # ========================================================
        # SAVE NEW OWNER ROLE
        # ========================================================

        set_owner_role(
            ctx.guild.id,
            role.id
        )


        # ========================================================
        # SUCCESS MESSAGE
        # ========================================================

        if current_role_id is None:

            await ctx.send(
                f"🔻 👑 {role.mention} is now the "
                "**Owner Role**.\n\n"
                "Members with this role can use the "
                "commands configured for the Owner Role."
            )

            return


        # ========================================================
        # FIND OLD ROLE
        # ========================================================

        old_role = ctx.guild.get_role(
            current_role_id
        )


        if old_role is not None:

            old_role_text = old_role.mention

        else:

            old_role_text = f"`{current_role_id}`"


        # ========================================================
        # UPDATED
        # ========================================================

        await ctx.send(
            "🔻 👑 **Owner Role updated.**\n\n"
            f"**Old:** {old_role_text}\n"
            f"**New:** {role.mention}"
        )


async def setup(bot):

    await bot.add_cog(
        SignOwnerModule(bot)
    )