from permissions import signed_permission

import discord
from discord.ext import commands

from modules.general.emoji import EMOJIS


class NicknameModule(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    # ========================================================
    # NICKNAME
    # ========================================================

    @commands.command()
    @signed_permission()
    @commands.bot_has_permissions(
        manage_nicknames=True
    )
    async def nickname(
        self,
        ctx,
        member: discord.Member,
        *,
        nickname=None
    ):

        # ====================================================
        # SERVER OWNER
        # ====================================================

        if member == ctx.guild.owner:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                "You cannot change the server owner's nickname."
            )

            return


        # ====================================================
        # ROLE HIERARCHY
        # ====================================================

        if (
            ctx.author != ctx.guild.owner
            and member.top_role >= ctx.author.top_role
        ):

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                "You cannot change the nickname of a member "
                "with an equal or higher role."
            )

            return


        # ====================================================
        # BOT ROLE HIERARCHY
        # ====================================================

        if member.top_role >= ctx.guild.me.top_role:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                "My role is not high enough to change "
                "this member's nickname."
            )

            return


        # ====================================================
        # CHANGE NICKNAME
        # ====================================================

        try:

            await member.edit(
                nick=nickname,
                reason=(
                    f"Nickname changed by {ctx.author}"
                )
            )


            # =================================================
            # RESET
            # =================================================

            if nickname is None:

                await ctx.send(
                    f"{EMOJIS['highlight']} "
                    f"{EMOJIS['true']} "
                    f"Reset {member.mention}'s nickname."
                )

            # =================================================
            # CHANGE
            # =================================================

            else:

                await ctx.send(
                    f"{EMOJIS['highlight']} "
                    f"{EMOJIS['true']} "
                    f"Changed {member.mention}'s nickname "
                    f"to `{nickname}`."
                )


        # ====================================================
        # FORBIDDEN
        # ====================================================

        except discord.Forbidden:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                "I do not have permission to change "
                "this member's nickname."
            )


        # ====================================================
        # HTTP ERROR
        # ====================================================

        except discord.HTTPException:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                "Failed to change this member's nickname."
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        NicknameModule(bot)
    )