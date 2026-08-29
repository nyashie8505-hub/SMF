import discord

from discord.ext import commands

from permissions import signed_permission


class SlowmodeModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @signed_permission()
    @commands.bot_has_permissions(
        manage_channels=True
    )
    async def slowmode(
        self,
        ctx,
        value: str
    ):

        # ========================================================
        # PARSE VALUE
        # ========================================================

        value = value.lower().strip()

        if value == "off":

            seconds = 0

        else:

            try:

                seconds = int(value)

            except ValueError:

                await ctx.send(
                    "🔻 ❌ Please enter a number of "
                    "seconds or `off`."
                )

                return

        # ========================================================
        # VALIDATE
        # ========================================================

        if seconds < 0:

            await ctx.send(
                "🔻 ❌ Slowmode cannot be negative."
            )

            return

        if seconds > 21600:

            await ctx.send(
                "🔻 ❌ Slowmode cannot exceed "
                "21600 seconds."
            )

            return

        # ========================================================
        # CHANGE SLOWMODE
        # ========================================================

        try:

            await ctx.channel.edit(
                slowmode_delay=seconds,
                reason=(
                    f"Slowmode changed by {ctx.author}"
                )
            )

        except discord.Forbidden:

            await ctx.send(
                "🔻 ❌ I do not have permission "
                "to change slowmode."
            )

            return

        except discord.HTTPException:

            await ctx.send(
                "🔻 ❌ An error occurred while "
                "changing slowmode."
            )

            return

        # ========================================================
        # MODLOG
        # ========================================================

        logger = self.bot.get_cog(
            "ModLogModule"
        )

        if logger:

            if seconds == 0:

                details = (
                    f"Channel: {ctx.channel.mention}\n"
                    "Slowmode disabled."
                )

            else:

                details = (
                    f"Channel: {ctx.channel.mention}\n"
                    f"Slowmode: `{seconds}` second(s)."
                )

            await logger.log_action(
                guild=ctx.guild,
                action="slowmode",
                moderator=ctx.author,
                details=details
            )

        # ========================================================
        # CONFIRMATION
        # ========================================================

        if seconds == 0:

            await ctx.send(
                "🔻 🔓 Slowmode has been disabled."
            )

            return

        await ctx.send(
            f"🔻 🐢 Slowmode has been set to "
            f"`{seconds}` second(s)."
        )


async def setup(bot):

    await bot.add_cog(
        SlowmodeModule(bot)
    )