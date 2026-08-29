from permissions import signed_permission
import discord
from discord.ext import commands


class NicknameModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


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

        if member == ctx.guild.owner:

            await ctx.send(
                "🔻 ❌ You cannot change the server owner's nickname."
            )

            return


        if (
            ctx.author != ctx.guild.owner
            and member.top_role >= ctx.author.top_role
        ):

            await ctx.send(
                "🔻 ❌ You cannot change the nickname of a member "
                "with an equal or higher role."
            )

            return


        if member.top_role >= ctx.guild.me.top_role:

            await ctx.send(
                "🔻 ❌ My role is not high enough "
                "to change this member's nickname."
            )

            return


        try:

            await member.edit(
                nick=nickname,
                reason=(
                    f"Nickname changed by {ctx.author}"
                )
            )


            if nickname is None:

                await ctx.send(
                    f"🔻 ✅ Reset {member.mention}'s nickname."
                )

            else:

                await ctx.send(
                    f"🔻 ✅ Changed {member.mention}'s nickname "
                    f"to `{nickname}`."
                )


        except discord.Forbidden:

            await ctx.send(
                "🔻 ❌ I do not have permission "
                "to change this member's nickname."
            )


        except discord.HTTPException:

            await ctx.send(
                "🔻 ❌ Failed to change this member's nickname."
            )


async def setup(bot):

    await bot.add_cog(
        NicknameModule(bot)
    )