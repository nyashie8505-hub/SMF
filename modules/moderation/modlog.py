import discord
from modules.general.emoji import EMOJIS

from discord.ext import commands, tasks

from database import (
    get_modlog_channels,
    add_modlog_channel,
    is_modlog_channel,
    is_modlog_command_disabled,
    disable_modlog_command,
    enable_modlog_command,
)

from permissions import signed_permission


class ModLogModule(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        # ========================================================
        # AUDIT LOG CACHE
        # ========================================================
        #
        # Stores the newest Audit Log ID per guild.
        #
        # This prevents old Audit Logs from being sent when
        # the bot starts.
        #

        self.last_audit_log_ids = {}

        # ========================================================
        # RECENT DIRECT ACTION CACHE
        # ========================================================
        #
        # Moderation modules such as timeout.py can call:
        #
        #     await logger.log_action(...)
        #
        # Discord will then also create an Audit Log entry.
        #
        # Without this cache, the same action would be logged twice:
        #
        # 1. Direct logger
        # 2. Audit Log watcher
        #
        # This cache allows the Audit Log watcher to recognize
        # actions already logged directly by this bot.
        #

        self.recent_direct_actions = {}

        # ========================================================
        # START AUDIT LOG WATCHER
        # ========================================================

        self.audit_log_watcher.start()

    # ============================================================
    # CLEANUP
    # ============================================================

    def cog_unload(self):

        self.audit_log_watcher.cancel()

    # ============================================================
    # BOT MESSAGE
    # ============================================================

    @staticmethod
    def bot_message(text):

        return f"{EMOJIS['highlight']} {text}"

    # ============================================================
    # ACTION TITLES
    # ============================================================

    ACTION_TITLES = {

        "ban":
            "Member Banned",

        "unban":
            "Member Unbanned",

        "kick":
            "Member Kicked",

        "timeout":
            "Member Timed Out",

        "untimeout":
            "Timeout Removed",

        "warn":
            "Member Warned",

        "unwarn":
            "Warning Removed",

        "clearwarning":
            "Warnings Cleared",

        "purge":
            "Messages Purged",

        "slowmode":
            "Slowmode Updated",

        "channel_create":
            "Channel Created",

        "channel_update":
            "Channel Updated",

        "channel_delete":
            "Channel Deleted",

        "role_create":
            "Role Created",

        "role_update":
            "Role Updated",

        "role_delete":
            "Role Deleted",

        "message_delete":
            "Message Deleted",

        "message_bulk_delete":
            "Messages Bulk Deleted",

        "message_pin":
            "Message Pinned",

        "message_unpin":
            "Message Unpinned",

        "member_update":
            "Member Updated",

        "guild_update":
            "Server Updated",

        "webhook_create":
            "Webhook Created",

        "webhook_update":
            "Webhook Updated",

        "webhook_delete":
            "Webhook Deleted",

        "emoji_create":
            "Emoji Created",

        "emoji_update":
            "Emoji Updated",

        "emoji_delete":
            "Emoji Deleted",
    }

    # ============================================================
    # COMMAND NAMES THAT CAN BE CONFIGURED
    # ============================================================

    SUPPORTED_ACTIONS = {

        "ban",
        "unban",
        "kick",
        "timeout",
        "untimeout",
        "warn",
        "unwarn",
        "clearwarning",
        "purge",
        "slowmode",

        "channel_create",
        "channel_update",
        "channel_delete",

        "role_create",
        "role_update",
        "role_delete",

        "message_delete",
        "message_bulk_delete",
        "message_pin",
        "message_unpin",

        "member_update",
        "guild_update",

        "webhook_create",
        "webhook_update",
        "webhook_delete",

        "emoji_create",
        "emoji_update",
        "emoji_delete",
    }

    # ============================================================
    # AUDIT LOG ACTION NAMES
    # ============================================================

    AUDIT_ACTION_NAMES = {

        discord.AuditLogAction.ban:
            "ban",

        discord.AuditLogAction.unban:
            "unban",

        discord.AuditLogAction.kick:
            "kick",

        discord.AuditLogAction.member_update:
            "member_update",

        discord.AuditLogAction.channel_create:
            "channel_create",

        discord.AuditLogAction.channel_update:
            "channel_update",

        discord.AuditLogAction.channel_delete:
            "channel_delete",

        discord.AuditLogAction.role_create:
            "role_create",

        discord.AuditLogAction.role_update:
            "role_update",

        discord.AuditLogAction.role_delete:
            "role_delete",

        discord.AuditLogAction.message_delete:
            "message_delete",

        discord.AuditLogAction.message_bulk_delete:
            "message_bulk_delete",

        discord.AuditLogAction.message_pin:
            "message_pin",

        discord.AuditLogAction.message_unpin:
            "message_unpin",

        discord.AuditLogAction.guild_update:
            "guild_update",

        discord.AuditLogAction.webhook_create:
            "webhook_create",

        discord.AuditLogAction.webhook_update:
            "webhook_update",

        discord.AuditLogAction.webhook_delete:
            "webhook_delete",

        discord.AuditLogAction.emoji_create:
            "emoji_create",

        discord.AuditLogAction.emoji_update:
            "emoji_update",

        discord.AuditLogAction.emoji_delete:
            "emoji_delete",
    }

    # ============================================================
    # GET ACTION TITLE
    # ============================================================

    def get_action_title(self, action):

        return self.ACTION_TITLES.get(
            action,
            action.replace("_", " ").title()
        )

    # ============================================================
    # FORMAT USER
    # ============================================================

    @staticmethod
    def format_user(user):

        if user is None:
            return "Unknown"

        mention = getattr(
            user,
            "mention",
            str(user)
        )

        user_id = getattr(
            user,
            "id",
            "Unknown"
        )

        return f"{mention} `{user_id}`"

    # ============================================================
    # CREATE EMBED
    # ============================================================

    def create_embed(
        self,
        action,
        target=None,
        moderator=None,
        reason=None,
        details=None
    ):

        title = self.get_action_title(
            action
        )

        embed = discord.Embed(
            title=f"{EMOJIS['highlight']} {title}",
            timestamp=discord.utils.utcnow()
        )

        # ========================================================
        # TARGET
        # ========================================================

        if target is not None:

            embed.add_field(
                name="User",
                value=self.format_user(target),
                inline=False
            )

        # ========================================================
        # MODERATOR
        # ========================================================

        if moderator is not None:

            embed.add_field(
                name="Moderator",
                value=self.format_user(moderator),
                inline=False
            )

        # ========================================================
        # REASON
        # ========================================================

        if reason:

            embed.add_field(
                name="Reason",
                value=str(reason)[:1024],
                inline=False
            )

        # ========================================================
        # DETAILS
        # ========================================================

        if details:

            embed.add_field(
                name="Details",
                value=str(details)[:1024],
                inline=False
            )

        # ========================================================
        # FOOTER
        # ========================================================

        embed.set_footer(
            text=f"Action: {action}"
        )

        return embed

    # ============================================================
    # REMEMBER DIRECT ACTION
    # ============================================================

    def remember_direct_action(
        self,
        guild_id,
        action,
        target_id
    ):

        if target_id is None:
            return

        key = (
            guild_id,
            str(action).lower(),
            int(target_id)
        )

        self.recent_direct_actions[key] = (
            discord.utils.utcnow()
        )

    # ============================================================
    # CHECK DIRECT ACTION
    # ============================================================

    def is_recent_direct_action(
        self,
        guild_id,
        action,
        target_id
    ):

        if target_id is None:
            return False

        key = (
            guild_id,
            str(action).lower(),
            int(target_id)
        )

        timestamp = self.recent_direct_actions.get(
            key
        )

        if timestamp is None:
            return False

        elapsed = (
            discord.utils.utcnow() - timestamp
        ).total_seconds()

        # ========================================================
        # 10 SECOND DEDUPLICATION WINDOW
        # ========================================================

        if elapsed <= 10:

            del self.recent_direct_actions[key]

            return True

        # ========================================================
        # EXPIRED CACHE ENTRY
        # ========================================================

        del self.recent_direct_actions[key]

        return False

    # ============================================================
    # SEND LOG
    # ============================================================

    async def send_log(
        self,
        guild,
        action,
        target=None,
        moderator=None,
        reason=None,
        details=None
    ):

        if guild is None:
            return

        action = str(action).lower()

        # ========================================================
        # GET MODLOG CHANNELS
        # ========================================================

        rows = get_modlog_channels(
            guild.id
        )

        if not rows:
            return

        # ========================================================
        # CREATE EMBED
        # ========================================================

        embed = self.create_embed(
            action=action,
            target=target,
            moderator=moderator,
            reason=reason,
            details=details
        )

        # ========================================================
        # SEND TO ALL MODLOG CHANNELS
        # ========================================================

        for row in rows:

            channel_id = row["channel_id"]

            # ====================================================
            # CHECK COMMAND FILTER
            # ====================================================

            if is_modlog_command_disabled(
                guild.id,
                channel_id,
                action
            ):

                continue

            # ====================================================
            # GET CHANNEL
            # ====================================================

            channel = guild.get_channel(
                channel_id
            )

            if channel is None:
                continue

            # ====================================================
            # SEND EMBED
            # ====================================================

            try:

                await channel.send(
                    embed=embed
                )

            except (
                discord.Forbidden,
                discord.NotFound,
                discord.HTTPException
            ):

                continue

    # ============================================================
    # PUBLIC LOGGER
    # ============================================================

    async def log_action(
        self,
        guild,
        action,
        target=None,
        moderator=None,
        reason=None,
        details=None
    ):

        action = str(action).lower()

        # ========================================================
        # REMEMBER THIS ACTION
        # ========================================================
        #
        # The action is being logged directly by this bot.
        #
        # Discord will usually create an Audit Log entry for it.
        # The watcher will use this cache to prevent a duplicate.
        #

        target_id = getattr(
            target,
            "id",
            None
        )

        self.remember_direct_action(
            guild_id=guild.id if guild else None,
            action=action,
            target_id=target_id
        )

        # ========================================================
        # SEND DIRECT LOG
        # ========================================================

        await self.send_log(
            guild=guild,
            action=action,
            target=target,
            moderator=moderator,
            reason=reason,
            details=details
        )

    # ============================================================
    # FIND LOGGER
    # ============================================================

    @staticmethod
    def get_logger(bot):

        return bot.get_cog(
            "ModLogModule"
        )

    # ============================================================
    # TIMEOUT DETECTION
    # ============================================================

    @staticmethod
    def is_timeout_entry(entry):

        if (
            entry.action
            != discord.AuditLogAction.member_update
        ):

            return False

        before = getattr(
            entry,
            "before",
            None
        )

        after = getattr(
            entry,
            "after",
            None
        )

        if before is None or after is None:
            return False

        before_timeout = getattr(
            before,
            "timed_out_until",
            None
        )

        after_timeout = getattr(
            after,
            "timed_out_until",
            None
        )

        return before_timeout != after_timeout

    # ============================================================
    # GET AUDIT ACTION NAME
    # ============================================================

    def get_audit_action_name(self, entry):

        # ========================================================
        # TIMEOUT / UNTIMEOUT
        # ========================================================

        if self.is_timeout_entry(entry):

            before = getattr(
                entry.before,
                "timed_out_until",
                None
            )

            after = getattr(
                entry.after,
                "timed_out_until",
                None
            )

            if (
                before is None
                and after is not None
            ):

                return "timeout"

            if (
                before is not None
                and after is None
            ):

                return "untimeout"

            return "timeout"

        # ========================================================
        # NORMAL AUDIT ACTION
        # ========================================================

        return self.AUDIT_ACTION_NAMES.get(
            entry.action
        )

    # ============================================================
    # PROCESS AUDIT ENTRY
    # ============================================================

    async def process_audit_entry(
        self,
        entry
    ):

        guild = entry.guild

        if guild is None:
            return

        # ========================================================
        # MODERATOR
        # ========================================================

        moderator = entry.user

        # ========================================================
        # IGNORE ACTIONS PERFORMED BY THIS BOT
        # ========================================================

        if (
            moderator is not None
            and self.bot.user is not None
            and moderator.id == self.bot.user.id
        ):

            return

        # ========================================================
        # ACTION
        # ========================================================

        action = self.get_audit_action_name(
            entry
        )

        if action is None:
            return

        # ========================================================
        # TARGET
        # ========================================================

        target = entry.target

        target_id = getattr(
            target,
            "id",
            None
        )

        # ========================================================
        # DEDUPLICATE DIRECT BOT ACTIONS
        # ========================================================
        #
        # Example:
        #
        # timeout.py
        #     ↓
        # logger.log_action()
        #     ↓
        # direct embed
        #
        # Discord Audit Log
        #     ↓
        # watcher
        #     ↓
        # THIS CHECK
        #     ↓
        # ignored
        #

        if self.is_recent_direct_action(
            guild_id=guild.id,
            action=action,
            target_id=target_id
        ):

            return

        # ========================================================
        # REASON
        # ========================================================

        reason = entry.reason

        # ========================================================
        # DETAILS
        # ========================================================

        details = None

        # ========================================================
        # TIMEOUT
        # ========================================================

        if action == "timeout":

            after = getattr(
                entry,
                "after",
                None
            )

            timeout_until = getattr(
                after,
                "timed_out_until",
                None
            )

            if timeout_until:

                details = (
                    "Until: "
                    f"<t:{int(timeout_until.timestamp())}:F>"
                )

        # ========================================================
        # UNTIMEOUT
        # ========================================================

        elif action == "untimeout":

            details = (
                "The timeout was removed."
            )

        # ========================================================
        # SEND AUDIT LOG EMBED
        # ========================================================

        await self.send_log(
            guild=guild,
            action=action,
            target=target,
            moderator=moderator,
            reason=reason,
            details=details
        )

    # ============================================================
    # AUDIT LOG WATCHER
    # ============================================================

    @tasks.loop(seconds=2)
    async def audit_log_watcher(self):

        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:

            try:

                # =================================================
                # ONLY WATCH SERVERS WITH MODLOG
                # =================================================

                rows = get_modlog_channels(
                    guild.id
                )

                if not rows:
                    continue

                # =================================================
                # GET RECENT AUDIT LOGS
                # =================================================

                entries = []

                async for entry in guild.audit_logs(
                    limit=20
                ):

                    entries.append(
                        entry
                    )

                if not entries:
                    continue

                # =================================================
                # AUDIT LOGS ARE NEWEST FIRST
                # =================================================

                entries.reverse()

                # =================================================
                # FIRST RUN
                #
                # Don't dump old logs.
                # =================================================

                if guild.id not in self.last_audit_log_ids:

                    self.last_audit_log_ids[
                        guild.id
                    ] = max(
                        entry.id
                        for entry in entries
                    )

                    continue

                # =================================================
                # LAST PROCESSED ID
                # =================================================

                last_id = self.last_audit_log_ids[
                    guild.id
                ]

                # =================================================
                # FIND NEW ENTRIES
                # =================================================

                new_entries = [
                    entry
                    for entry in entries
                    if entry.id > last_id
                ]

                # =================================================
                # UPDATE CACHE
                # =================================================

                self.last_audit_log_ids[
                    guild.id
                ] = max(
                    entry.id
                    for entry in entries
                )

                # =================================================
                # PROCESS NEW ENTRIES
                # =================================================

                for entry in new_entries:

                    try:

                        await self.process_audit_entry(
                            entry
                        )

                    except Exception as error:

                        print(
                            "[ModLog] Failed to process "
                            f"audit entry {entry.id}: {error}"
                        )

            except discord.Forbidden:

                # Missing View Audit Log permission.
                continue

            except discord.NotFound:

                continue

            except discord.HTTPException:

                continue

            except Exception as error:

                print(
                    "[ModLog] Audit watcher error "
                    f"in {guild.name}: {error}"
                )

    # ============================================================
    # LOOP READY
    # ============================================================

    @audit_log_watcher.before_loop
    async def before_audit_log_watcher(self):

        await self.bot.wait_until_ready()

    # ============================================================
    # MODLOG COMMAND
    #
    # duModlog
    #
    # duModlog #channel
    #
    # duModlog on ban #channel
    #
    # duModlog off ban #channel
    #
    # ============================================================

    @commands.command(
        name="modlog"
    )
    @commands.guild_only()
    @signed_permission()
    async def modlog(
        self,
        ctx,
        action=None,
        command_name=None,
        channel: discord.TextChannel = None
    ):

        # ========================================================
        # duModlog
        #
        # SHOW ALL MODLOG CHANNELS
        # ========================================================

        if action is None:

            rows = get_modlog_channels(
                ctx.guild.id
            )

            if not rows:

                await ctx.send(
                    self.bot_message(
                        "There are currently no channels "
                        "with ModLog enabled."
                    )
                )

                return

            channels = []

            for row in rows:

                target_channel = ctx.guild.get_channel(
                    row["channel_id"]
                )

                if target_channel is not None:

                    channels.append(
                        target_channel.mention
                    )

            if not channels:

                await ctx.send(
                    self.bot_message(
                        "There are currently no channels "
                        "with ModLog enabled."
                    )
                )

                return

            await ctx.send(
                self.bot_message(
                    "**Channels with ModLog:**\n"
                    + "\n".join(
                        f"• {channel}"
                        for channel in channels
                    )
                )
            )

            return

        # ========================================================
        # duModlog #channel
        #
        # ENABLE MODLOG IN CHANNEL
        # ========================================================

        if (
            action.startswith("<#")
            and action.endswith(">")
        ):

            try:

                channel_id = int(
                    action[2:-1]
                )

            except ValueError:

                await ctx.send(
                    self.bot_message(
                        "Invalid channel."
                    )
                )

                return

            target_channel = ctx.guild.get_channel(
                channel_id
            )

            if target_channel is None:

                await ctx.send(
                    self.bot_message(
                        "I could not find that channel."
                    )
                )

                return

            if is_modlog_channel(
                ctx.guild.id,
                target_channel.id
            ):

                await ctx.send(
                    self.bot_message(
                        f"{target_channel.mention} "
                        "already has ModLog enabled."
                    )
                )

                return

            add_modlog_channel(
                ctx.guild.id,
                target_channel.id
            )

            await ctx.send(
                self.bot_message(
                    f"ModLog has been enabled in "
                    f"{target_channel.mention}."
                )
            )

            return

        # ========================================================
        # duModlog on [command] #channel
        # ========================================================

        if action.lower() == "on":

            if (
                command_name is None
                or channel is None
            ):

                await ctx.send(
                    self.bot_message(
                        "Usage: "
                        "`duModlog on [command] #channel`"
                    )
                )

                return

            command_name = command_name.lower()

            # ====================================================
            # VALID COMMAND
            # ====================================================

            if command_name not in self.SUPPORTED_ACTIONS:

                await ctx.send(
                    self.bot_message(
                        f"Unknown ModLog action `{command_name}`."
                    )
                )

                return

            # ====================================================
            # CHANNEL MUST BE MODLOG
            # ====================================================

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

            # ====================================================
            # ALREADY ENABLED
            # ====================================================

            if not is_modlog_command_disabled(
                ctx.guild.id,
                channel.id,
                command_name
            ):

                await ctx.send(
                    self.bot_message(
                        "This command is still logging."
                    )
                )

                return

            # ====================================================
            # ENABLE
            # ====================================================

            enable_modlog_command(
                ctx.guild.id,
                channel.id,
                command_name
            )

            await ctx.send(
                self.bot_message(
                    f"Logging for `{command_name}` has been "
                    f"enabled in {channel.mention}."
                )
            )

            return

        # ========================================================
        # duModlog off [command] #channel
        # ========================================================

        if action.lower() == "off":

            if (
                command_name is None
                or channel is None
            ):

                await ctx.send(
                    self.bot_message(
                        "Usage: "
                        "`duModlog off [command] #channel`"
                    )
                )

                return

            command_name = command_name.lower()

            # ====================================================
            # VALID COMMAND
            # ====================================================

            if command_name not in self.SUPPORTED_ACTIONS:

                await ctx.send(
                    self.bot_message(
                        f"Unknown ModLog action `{command_name}`."
                    )
                )

                return

            # ====================================================
            # CHANNEL MUST BE MODLOG
            # ====================================================

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

            # ====================================================
            # ALREADY DISABLED
            # ====================================================

            if is_modlog_command_disabled(
                ctx.guild.id,
                channel.id,
                command_name
            ):

                await ctx.send(
                    self.bot_message(
                        f"Logging for `{command_name}` is already "
                        f"disabled in {channel.mention}."
                    )
                )

                return

            # ====================================================
            # DISABLE
            # ====================================================

            disable_modlog_command(
                ctx.guild.id,
                channel.id,
                command_name
            )

            await ctx.send(
                self.bot_message(
                    f"Logging for `{command_name}` has been "
                    f"disabled in {channel.mention}."
                )
            )

            return

        # ========================================================
        # INVALID USAGE
        # ========================================================

        await ctx.send(
            self.bot_message(
                "**Invalid ModLog command.**\n\n"
                "`duModlog` — View ModLog channels\n"
                "`duModlog #channel` — Enable ModLog\n"
                "`duModlog on [command] #channel` — Enable logging\n"
                "`duModlog off [command] #channel` — Disable logging"
            )
        )


# ================================================================
# SETUP
# ================================================================

async def setup(bot):

    await bot.add_cog(
        ModLogModule(bot)
    )
