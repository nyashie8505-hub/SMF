import discord
from discord.ext import commands

from modules.general.emoji import EMOJIS


# ============================================================
# COMMAND INFORMATION
# ============================================================
#
# Command names are stored WITHOUT the "du" prefix.
#
# You can edit:
#   description
#   usage
#   example
#   permission
#
# ============================================================


COMMAND_INFO = {

    # ========================================================
    # GENERAL
    # ========================================================

    "ping": {
        "description": "Check the bot's latency and connection status.",
        "usage": "duping",
        "example": "duping",
        "permission": "Everyone",
        "category": "general",
    },

    "patchnote": {
        "description": "View the latest S.M.F patch notes.",
        "usage": "dupatch",
        "example": "dupatch",
        "permission": "DSA owners",
        "category": "general",
    },

    "serverstatus": {
        "description": "Display information and statistics about the server.",
        "usage": "duserverstatus",
        "example": "duserverstatus",
        "permission": "Signed roles",
        "category": "general",
    },

    "serverstat": {
        "description": "Display server information and statistics now (does not auto-update).",
        "usage": "dusvstat",
        "example": "dusvstat",
        "permission": "Everyone",
        "category": "general",
    },

    "status": {
        "description": "Display status information about a user.",
        "usage": "dustatus <user> / ID [channel]",
        "example": "dustatus @User / ID #general",
        "permission": "Everyone",
        "category": "general",
    },

    "tup": {
        "description": "Send a message through the bot.",
        "usage": "dutup <message>",
        "example": "dutup Hello everyone!",
        "permission": "Signed Role",
        "category": "general",
    },


    # ========================================================
    # MODERATION
    # ========================================================

    "ban": {
        "description": "Ban a member from the server.",
        "usage": "duban <member> [reason]",
        "example": "duban @User Breaking the rules",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "banlist": {
        "description": "Display the members currently banned from the server.",
        "usage": "dubanlist",
        "example": "dubanlist",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "clearwarning": {
        "description": "Clear all warnings from a member.",
        "usage": "duclearwarning <member>",
        "example": "duclearwarning @User",
        "permission": "Server Owner,  Owner Role, or Signed Role",
        "category": "moderation",
    },

    "kick": {
        "description": "Kick a member from the server.",
        "usage": "dukick <member> [reason]",
        "example": "dukick @User Breaking the rules",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "lock": {
        "description": "Lock a channel and prevent members from sending messages.",
        "usage": "dulock",
        "example": "dulock",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "modlog": {
        "description": "Configure and manage the server moderation log.",
        "usage": "dumodlog <on|off> [channel]",
        "example": "dumodlog on #mod-log",
        "permission": "Server Owner, Owner Role",
        "category": "moderation",
    },

    "modlog": {
        "description": "Display mod log channels.",
        "usage": "dumodlog",
        "example": "dumodlog",
        "permission": "Server Owner, Owner Role",
        "category": "moderation",
    },

    "nickname": {
        "description": "Change a member's nickname.",
        "usage": "dunickname <member> <nickname>",
        "example": "dunickname @User Cool Name",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "purge": {
        "description": "Delete multiple messages from a channel.",
        "usage": "dupurge <member>(option) <amount>",
        "example": "dupurge 20",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "sign": {
        "description": "Grant a lower role permission to use a command.",
        "usage": "dusign <role> <command>",
        "example": "dusign @Moderator warn/all",
        "permission": "Server Owner, Owner Role, Management Role",
        "category": "moderation",
    },

    "signlist": {
        "description": "Display the commands signed to a equal role.",
        "usage": "dusignlist <role>",
        "example": "dusignlist @Moderator",
        "permission": "Server Owner, Owner Role, Everyone",
        "category": "moderation",
    },

    "signowner": {
        "description": "Set the server Owner Role.",
        "usage": "dusignowner <role>",
        "example": "dusignowner @Owner",
        "permission": "Server Owner only",
        "category": "moderation",
    },

    "slowmode": {
        "description": "Set the slowmode delay for a channel.",
        "usage": "duslowmode <seconds>",
        "example": "duslowmode 10",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "timeout": {
        "description": "Timeout a member for a specified duration.",
        "usage": "duntimeout <member> <duration> [reason]",
        "example": "duntimeout @User 10m Spamming",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "timeoutlist": {
        "description": "Display members currently in timeout.",
        "usage": "duntimeoutlist",
        "example": "duntimeoutlist",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "unban": {
        "description": "Unban a user from the server.",
        "usage": "duunban <user_id>",
        "example": "duunban 123456789012345678",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "unlock": {
        "description": "Unlock a channel and allow members to send messages.",
        "usage": "duunlock",
        "example": "duunlock",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "unsign": {
        "description": "Remove a signed command permission from a role.",
        "usage": "duunsign <role> <command>",
        "example": "duunsign @Moderator warn",
        "permission": "Server Owner, Owner Role",
        "category": "moderation",
    },

    "untimeout": {
        "description": "Remove a timeout from a member.",
        "usage": "duuntimeout <member> [reason]",
        "example": "duuntimeout @User Timeout appeal accepted",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "unwarn": {
        "description": "Remove a warning from a member.",
        "usage": "duunwarn <member>",
        "example": "duunwarn @User",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "warn": {
        "description": "Issue a warning to a member.",
        "usage": "duwarn <member> [reason]",
        "example": "duwarn @User Spamming messages",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

    "warnlist": {
        "description": "Display the warnings of a member.",
        "usage": "duwarnlist <member>",
        "example": "duwarnlist @User",
        "permission": "Server Owner, Owner Role, or Signed Role",
        "category": "moderation",
    },

}


# ============================================================
# HELP MODULE
# ============================================================


class HelpModule(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot


    # ========================================================
    # FORMAT COMMAND NAME
    # ========================================================

    def format_command_name(
        self,
        command_name
    ):

        command_name = command_name.lower().strip()

        if command_name.startswith("du"):

            command_name = command_name[2:]

        return command_name


    # ========================================================
    # GET COMMAND INFO
    # ========================================================

    def get_command_info(
        self,
        command_name
    ):

        command_name = self.format_command_name(
            command_name
        )

        return COMMAND_INFO.get(
            command_name
        )


    # ========================================================
    # BUILD COMMAND LIST
    # ========================================================

    def build_command_list(
        self,
        category
    ):

        command_list = []

        for name, info in COMMAND_INFO.items():

            if info["category"] != category:

                continue

            command_list.append(
                f"{EMOJIS['highlight']} "
                f"`du{name}` — "
                f"{info['description']}"
            )

        return command_list


    # ========================================================
    # ADD SECTION SAFELY
    # ========================================================
    #
    # Discord limits an embed field value to 1024 characters.
    #
    # If a section becomes too long, it is automatically
    # split into multiple fields.
    #
    # Every field keeps the exact same title.
    #
    # ========================================================

    def add_section(
        self,
        embed,
        title,
        command_list
    ):

        chunks = []

        current_chunk = ""

        for line in command_list:

            # ------------------------------------------------
            # Calculate new length
            # ------------------------------------------------

            additional_length = len(line)

            if current_chunk:

                additional_length += 1

            # ------------------------------------------------
            # Start a new field if necessary
            # ------------------------------------------------

            if (
                len(current_chunk)
                + additional_length
                > 1024
            ):

                if current_chunk:

                    chunks.append(
                        current_chunk
                    )

                current_chunk = line

            # ------------------------------------------------
            # Add line to current field
            # ------------------------------------------------

            else:

                if current_chunk:

                    current_chunk += "\n"

                current_chunk += line


        # ====================================================
        # ADD LAST CHUNK
        # ====================================================

        if current_chunk:

            chunks.append(
                current_chunk
            )


        # ====================================================
        # CREATE EMBED FIELDS
        # ====================================================

        for chunk in chunks:

            embed.add_field(
                name=title,
                value=chunk,
                inline=False
            )


    # ========================================================
    # DUHELP
    # ========================================================

    @commands.command(
        name="help"
    )
    async def help_command(
        self,
        ctx
    ):

        # ====================================================
        # GENERAL COMMANDS
        # ====================================================

        general_commands = self.build_command_list(
            "general"
        )


        # ====================================================
        # MODERATION COMMANDS
        # ====================================================

        moderation_commands = self.build_command_list(
            "moderation"
        )


        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title=(
                f"{EMOJIS['highlight']} "
                "S.M.F Commands"
            ),
            description=(
                "Use `ducmdinfo <command>` to view "
                "detailed information about a command."
            )
        )


        # ====================================================
        # GENERAL SECTION
        # ====================================================

        if general_commands:

            self.add_section(
                embed,
                f"{EMOJIS['highlight']} General",
                general_commands
            )


        # ====================================================
        # MODERATION SECTION
        # ====================================================

        if moderation_commands:

            self.add_section(
                embed,
                f"{EMOJIS['highlight']} Moderation",
                moderation_commands
            )


        # ====================================================
        # SEND
        # ====================================================

        await ctx.send(
            embed=embed
        )


    # ========================================================
    # DUCMDINFO
    # ========================================================

    @commands.command(
        name="cmdinfo"
    )
    async def command_info(
        self,
        ctx,
        command_name: str = None
    ):

        # ====================================================
        # NO COMMAND
        # ====================================================

        if not command_name:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                "You must specify a command."
            )

            return


        # ====================================================
        # FIND COMMAND
        # ====================================================

        info = self.get_command_info(
            command_name
        )


        # ====================================================
        # COMMAND NOT FOUND
        # ====================================================

        if info is None:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"{EMOJIS['false']} "
                f"Command `{command_name}` was not found."
            )

            return


        # ====================================================
        # NORMALIZED NAME
        # ====================================================

        normalized_name = self.format_command_name(
            command_name
        )


        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title=(
                f"{EMOJIS['highlight']} "
                "Command Information"
            )
        )


        # ====================================================
        # COMMAND
        # ====================================================

        embed.add_field(
            name=f"{EMOJIS['highlight']} Command",
            value=f"`du{normalized_name}`",
            inline=False
        )


        # ====================================================
        # DESCRIPTION
        # ====================================================

        embed.add_field(
            name=f"{EMOJIS['highlight']} Description",
            value=info["description"],
            inline=False
        )


        # ====================================================
        # USAGE
        # ====================================================

        embed.add_field(
            name=f"{EMOJIS['highlight']} Usage",
            value=f"`{info['usage']}`",
            inline=False
        )


        # ====================================================
        # EXAMPLE
        # ====================================================

        embed.add_field(
            name=f"{EMOJIS['highlight']} Example",
            value=f"`{info['example']}`",
            inline=False
        )


        # ====================================================
        # PERMISSION
        # ====================================================

        embed.add_field(
            name=f"{EMOJIS['highlight']} Permission",
            value=info["permission"],
            inline=False
        )


        # ====================================================
        # SEND
        # ====================================================

        await ctx.send(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================


async def setup(
    bot
):

    await bot.add_cog(
        HelpModule(bot)
    )