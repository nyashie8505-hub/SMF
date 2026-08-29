import discord

from discord.ext import commands

from modules.general.emoji import EMOJIS

from database import (
    get_connection,
    get_owner_role
)


class ServerStatusModule(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        # ====================================================
        # STATUS MESSAGE STORAGE
        # guild_id -> (channel_id, message_id)
        # ====================================================

        self.status_messages = {}


    # ========================================================
    # CHECK SERVER STATUS PERMISSION
    # ========================================================

    async def has_serverstatus_permission(
        self,
        ctx
    ):

        if not ctx.guild:
            return False


        # ====================================================
        # SERVER OWNER
        # ====================================================

        if ctx.author.id == ctx.guild.owner_id:

            return True


        # ====================================================
        # OWNER ROLE
        # ====================================================

        owner_role_id = get_owner_role(
            ctx.guild.id
        )

        if owner_role_id is not None:

            if any(
                role.id == owner_role_id
                for role in ctx.author.roles
            ):

                return True


        # ====================================================
        # USER ROLES
        # ====================================================

        role_ids = [
            role.id
            for role in ctx.author.roles
        ]

        if not role_ids:

            return False


        # ====================================================
        # DATABASE
        # ====================================================

        connection = get_connection()
        cursor = connection.cursor()

        try:

            placeholders = ",".join(
                "%s" for _ in role_ids
            )


            cursor.execute(
                f"""
                SELECT 1
                FROM command_permissions
                WHERE guild_id = %s
                AND role_id IN ({placeholders})
                AND command_name IN (%s, %s)
                LIMIT 1
                """,
                (
                    ctx.guild.id,
                    *role_ids,
                    "serverstatus",
                    "all"
                )
            )


            result = cursor.fetchone()

            return result is not None


        finally:

            cursor.close()
            connection.close()


    # ========================================================
    # BUILD SERVER STATUS
    # ========================================================

    def build_status(
        self,
        guild
    ):

        # ====================================================
        # MEMBERS
        # ====================================================

        total_members = (
            guild.member_count or 0
        )


        bot_count = sum(
            1
            for member in guild.members
            if member.bot
        )


        member_count = (
            total_members - bot_count
        )


        # ====================================================
        # CHANNELS
        # ====================================================

        text_channels = len(
            guild.text_channels
        )


        voice_channels = len(
            guild.voice_channels
        )


        categories = len(
            guild.categories
        )


        # ====================================================
        # ROLES
        # ====================================================

        role_count = len(
            guild.roles
        )


        # ====================================================
        # EMOJIS
        # ====================================================

        emoji_count = len(
            guild.emojis
        )


        # ====================================================
        # OWNER
        # ====================================================

        if guild.owner:

            owner_text = guild.owner.name

        else:

            owner_text = "Unknown"


        # ====================================================
        # CREATED
        # ====================================================

        created_date = discord.utils.format_dt(
            guild.created_at,
            style="F"
        )


        # ====================================================
        # STATUS
        # ====================================================

        return (
            f"# {EMOJIS['highlight']} Server Status\n"
            f"\n"
            f"{EMOJIS['highlight']} 🏠 "
            f"Server: **{guild.name}**\n"
            f"\n"
            f"{EMOJIS['highlight']} 👥 "
            f"Total Members: `{total_members:,}`\n"
            f"👤 Members: `{member_count:,}`\n"
            f"🤖 Bots: `{bot_count:,}`\n"
            f"\n"
            f"{EMOJIS['highlight']} 💬 "
            f"Text Channels: `{text_channels:,}`\n"
            f"🔊 Voice Channels: `{voice_channels:,}`\n"
            f"📁 Categories: `{categories:,}`\n"
            f"🎭 Roles: `{role_count:,}`\n"
            f"😀 Emojis: `{emoji_count:,}`\n"
            f"\n"
            f"{EMOJIS['highlight']} 📅 "
            f"Created: {created_date}\n"
            f"\n"
            f"{EMOJIS['highlight']} 👑 "
            f"Owner: **{owner_text}**"
        )


    # ========================================================
    # DUSERVERSTATUS
    # ========================================================

    @commands.command()
    async def serverstatus(
        self,
        ctx
    ):

        # ====================================================
        # GUILD CHECK
        # ====================================================

        if ctx.guild is None:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                f"This command can only be used "
                f"in a server."
            )

            return


        # ====================================================
        # PERMISSION CHECK
        # ====================================================

        allowed = await self.has_serverstatus_permission(
            ctx
        )

        if not allowed:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                f"You are not signed to use "
                f"`duserverstatus`."
            )

            return


        # ====================================================
        # SEND STATUS
        # ====================================================

        message = await ctx.send(
            self.build_status(
                ctx.guild
            )
        )


        # ====================================================
        # SAVE MESSAGE
        # ====================================================

        self.status_messages[
            ctx.guild.id
        ] = (
            ctx.channel.id,
            message.id
        )


    # ========================================================
    # UPDATE STATUS
    # ========================================================

    async def update_status(
        self,
        guild
    ):

        status_data = self.status_messages.get(
            guild.id
        )

        if status_data is None:

            return


        channel_id, message_id = status_data


        # ====================================================
        # GET CHANNEL
        # ====================================================

        channel = guild.get_channel(
            channel_id
        )

        if channel is None:

            self.status_messages.pop(
                guild.id,
                None
            )

            return


        # ====================================================
        # EDIT MESSAGE
        # ====================================================

        try:

            message = await channel.fetch_message(
                message_id
            )


            await message.edit(
                content=self.build_status(
                    guild
                )
            )


        except (
            discord.NotFound,
            discord.Forbidden,
            discord.HTTPException
        ):

            self.status_messages.pop(
                guild.id,
                None
            )


    # ========================================================
    # MEMBER JOIN
    # ========================================================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):

        await self.update_status(
            member.guild
        )


    # ========================================================
    # MEMBER LEAVE
    # ========================================================

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member
    ):

        await self.update_status(
            member.guild
        )


    # ========================================================
    # CHANNEL CREATE
    # ========================================================

    @commands.Cog.listener()
    async def on_guild_channel_create(
        self,
        channel
    ):

        await self.update_status(
            channel.guild
        )


    # ========================================================
    # CHANNEL DELETE
    # ========================================================

    @commands.Cog.listener()
    async def on_guild_channel_delete(
        self,
        channel
    ):

        await self.update_status(
            channel.guild
        )


    # ========================================================
    # CHANNEL UPDATE
    # ========================================================

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self,
        before,
        after
    ):

        await self.update_status(
            after.guild
        )


    # ========================================================
    # ROLE CREATE
    # ========================================================

    @commands.Cog.listener()
    async def on_guild_role_create(
        self,
        role
    ):

        await self.update_status(
            role.guild
        )


    # ========================================================
    # ROLE DELETE
    # ========================================================

    @commands.Cog.listener()
    async def on_guild_role_delete(
        self,
        role
    ):

        await self.update_status(
            role.guild
        )


    # ========================================================
    # ROLE UPDATE
    # ========================================================

    @commands.Cog.listener()
    async def on_guild_role_update(
        self,
        before,
        after
    ):

        await self.update_status(
            after.guild
        )


    # ========================================================
    # EMOJI UPDATE
    # ========================================================

    @commands.Cog.listener()
    async def on_guild_emojis_update(
        self,
        guild,
        before,
        after
    ):

        await self.update_status(
            guild
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        ServerStatusModule(bot)
    )