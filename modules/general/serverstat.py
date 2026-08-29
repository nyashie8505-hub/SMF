import discord

from discord.ext import commands

from modules.general.emoji import EMOJIS


class ServerStatModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def svstat(self, ctx):

        # ========================================================
        # SERVER ONLY
        # ========================================================

        if ctx.guild is None:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"This command can only be used in a server."
            )

            return


        guild = ctx.guild


        # ========================================================
        # MEMBER STATISTICS
        # ========================================================

        total_members = guild.member_count

        bot_count = sum(
            1
            for member in guild.members
            if member.bot
        )

        member_count = (
            total_members - bot_count
        )


        # ========================================================
        # CHANNEL STATISTICS
        # ========================================================

        text_channels = len(
            guild.text_channels
        )

        voice_channels = len(
            guild.voice_channels
        )

        categories = len(
            guild.categories
        )


        # ========================================================
        # OTHER STATISTICS
        # ========================================================

        role_count = len(
            guild.roles
        )

        emoji_count = len(
            guild.emojis
        )


        # ========================================================
        # SERVER OWNER
        # ========================================================

        if guild.owner:

            owner_text = guild.owner.name

        else:

            owner_text = "Unknown"


        # ========================================================
        # SERVER CREATION DATE
        # ========================================================

        created_date = discord.utils.format_dt(
            guild.created_at,
            style="F"
        )


        # ========================================================
        # SERVER STATUS
        # ========================================================

        content = (
            f"# {EMOJIS['highlight']} Server Status\n"
            f"{EMOJIS['highlight']}\n"
            f"🏠 Server: **{guild.name}**\n"
            f"{EMOJIS['highlight']}\n"
            f"👥 Total Members: `{total_members:,}`\n"
            f"👤 Members: `{member_count:,}`\n"
            f"🤖 Bots: `{bot_count:,}`\n"
            f"{EMOJIS['highlight']}\n"
            f"💬 Text Channels: `{text_channels:,}`\n"
            f"🔊 Voice Channels: `{voice_channels:,}`\n"
            f"📁 Categories: `{categories:,}`\n"
            f"🎭 Roles: `{role_count:,}`\n"
            f"😀 Emojis: `{emoji_count:,}`\n"
            f"{EMOJIS['highlight']}\n"
            f"📅 Created:\n"
            f"{created_date}\n"
            f"{EMOJIS['highlight']}\n"
            f"👑 Owner: {owner_text}"
        )


        # ========================================================
        # SEND
        # ========================================================

        await ctx.send(
            content
        )


# ================================================================
# SETUP
# ================================================================

async def setup(bot):

    await bot.add_cog(
        ServerStatModule(bot)
    )