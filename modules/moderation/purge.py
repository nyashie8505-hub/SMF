import discord
from modules.general.emoji import EMOJIS

from discord.ext import commands

from permissions import signed_permission


class PurgeModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @signed_permission()
    @commands.bot_has_permissions(
        manage_messages=True
    )
    async def purge(
        self,
        ctx,
        amount: int,
        member: discord.Member = None
    ):

        # ========================================================
        # VALIDATE AMOUNT
        # ========================================================

        if amount <= 0:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} The amount must be greater than 0."
            )

            return

        if amount > 100:

            await ctx.send(
                "{EMOJIS['highlight']} {EMOJIS['false']} You can purge a maximum of "
                "100 messages at once."
            )

            return

        # ========================================================
        # PURGE ALL MESSAGES
        # ========================================================

        if member is None:

            try:

                deleted = await ctx.channel.purge(
                    limit=amount + 1
                )

            except discord.Forbidden:

                await ctx.send(
                    "{EMOJIS['highlight']} {EMOJIS['false']} I do not have permission "
                    "to delete messages."
                )

                return

            except discord.HTTPException:

                await ctx.send(
                    "{EMOJIS['highlight']} {EMOJIS['false']} An error occurred while "
                    "deleting messages."
                )

                return

            # The command itself is included.
            deleted_count = max(
                0,
                len(deleted) - 1
            )

        # ========================================================
        # PURGE MESSAGES FROM SPECIFIC MEMBER
        # ========================================================

        else:

            messages_to_delete = []

            async for message in ctx.channel.history(
                limit=None,
                oldest_first=False
            ):

                # Do not count command message.
                if message.id == ctx.message.id:
                    continue

                if message.author.id == member.id:

                    messages_to_delete.append(
                        message
                    )

                if len(messages_to_delete) >= amount:
                    break

            # ====================================================
            # NOTHING FOUND
            # ====================================================

            if not messages_to_delete:

                await ctx.send(
                    f"{EMOJIS['highlight']} {EMOJIS['false']} No messages from "
                    f"{member.mention} were found."
                )

                return

            deleted_count = len(
                messages_to_delete
            )

            # ====================================================
            # DELETE COMMAND
            # ====================================================

            try:

                await ctx.message.delete()

            except discord.HTTPException:

                pass

            # ====================================================
            # DELETE MESSAGES
            # ====================================================

            try:

                await ctx.channel.delete_messages(
                    messages_to_delete
                )

            except discord.Forbidden:

                await ctx.send(
                    "{EMOJIS['highlight']} {EMOJIS['false']} I do not have permission "
                    "to delete these messages."
                )

                return

            except discord.HTTPException:

                await ctx.send(
                    "{EMOJIS['highlight']} {EMOJIS['false']} An error occurred while "
                    "deleting messages."
                )

                return

        # ========================================================
        # MODLOG
        # ========================================================

        logger = self.bot.get_cog(
            "ModLogModule"
        )

        if logger:

            if member is None:

                details = (
                    f"Deleted messages: `{deleted_count}`\n"
                    f"Channel: {ctx.channel.mention}"
                )

            else:

                details = (
                    f"Deleted messages: `{deleted_count}`\n"
                    f"Message author: {member.mention}\n"
                    f"Channel: {ctx.channel.mention}"
                )

            await logger.log_action(
                guild=ctx.guild,
                action="purge",
                target=member,
                moderator=ctx.author,
                details=details
            )

        # ========================================================
        # CONFIRMATION
        # ========================================================

        confirmation = await ctx.send(
            f"{EMOJIS['highlight']} 🗑️ Deleted `{deleted_count}` "
            f"message(s)."
        )

        await confirmation.delete(
            delay=5
        )


async def setup(bot):

    await bot.add_cog(
        PurgeModule(bot)
    )