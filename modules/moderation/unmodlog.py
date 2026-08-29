import discord
from discord.ext import commands

from database import (
    is_modlog_channel,
    remove_modlog_channel,
    clear_disabled_modlog_commands,
)


class UnModLogModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def bot_message(text):
        return f"🔻 {text}"

    @commands.command(
        name="unmodlog"
    )
    @commands.guild_only()
    async def unmodlog(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        if not is_modlog_channel(
            ctx.guild.id,
            channel.id
        ):

            await ctx.send(
                self.bot_message(
                    f"{channel.mention} does not have "
                    "ModLog enabled."
                )
            )

            return

        remove_modlog_channel(
            ctx.guild.id,
            channel.id
        )

        clear_disabled_modlog_commands(
            ctx.guild.id,
            channel.id
        )

        await ctx.send(
            self.bot_message(
                f"ModLog has been disabled in "
                f"{channel.mention}."
            )
        )


async def setup(bot):

    await bot.add_cog(
        UnModLogModule(bot)
    )