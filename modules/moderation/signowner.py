import discord

from discord.ext import commands

from modules.general.emoji import EMOJIS

from database import get_owner_role, set_owner_role


class SignOwnerModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # ========================================================
    # SIGN OWNER
    # ========================================================

    @commands.command()
    async def signowner(
        self,
        ctx,
        role: discord.Role
    ):

        # ====================================================
        # GUILD CHECK
        # ====================================================

        if not ctx.guild:
            return


        # ====================================================
        # ONLY SERVER OWNER
        # ====================================================

        if ctx.author.id != ctx.guild.owner_id:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                f"Only the server owner can use "
                f"`dusignowner`."
            )

            return


        # ====================================================
        # ROLE VALIDATION
        # ====================================================

        # Cannot use @everyone

        if role.is_default():

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                f"You cannot use @everyone "
                f"as the Owner Role."
            )

            return


        # Cannot use managed/integration roles

        if role.managed:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                f"You cannot use a managed/integration "
                f"role as the Owner Role."
            )

            return


        # ====================================================
        # CURRENT OWNER ROLE
        # ====================================================

        current_role_id = get_owner_role(
            ctx.guild.id
        )


        # ====================================================
        # ALREADY OWNER ROLE
        # ====================================================

        if current_role_id == role.id:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                f"{role.mention} is already "
                f"the Owner Role."
            )

            return


        # ====================================================
        # SAVE NEW OWNER ROLE
        # ====================================================

        set_owner_role(
            ctx.guild.id,
            role.id
        )


        # ====================================================
        # FIRST OWNER ROLE
        # ====================================================

        if current_role_id is None:

            await ctx.send(
                f"{EMOJIS['highlight']} 👑 "
                f"{role.mention} is now the "
                f"**Owner Role**.\n\n"
                f"Members with this role can use the "
                f"commands configured for the Owner Role."
            )

            return


        # ====================================================
        # FIND OLD ROLE
        # ====================================================

        old_role = ctx.guild.get_role(
            current_role_id
        )


        if old_role is not None:

            old_role_text = old_role.mention

        else:

            old_role_text = f"`{current_role_id}`"


        # ====================================================
        # UPDATED
        # ====================================================

        await ctx.send(
            f"{EMOJIS['highlight']} 👑 "
            f"**Owner Role updated.**\n\n"
            f"**Old:** {old_role_text}\n"
            f"**New:** {role.mention}"
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        SignOwnerModule(bot)
    )