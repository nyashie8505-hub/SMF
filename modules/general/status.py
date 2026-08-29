import re
import discord

from discord.ext import commands

from modules.general.emoji import EMOJIS


# ================================================================
# URL DETECTION
# ================================================================

URL_PATTERN = re.compile(
    r"https?://\S+",
    re.IGNORECASE
)


# ================================================================
# STATUS MODULE
# ================================================================

class StatusModule(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    # ============================================================
    # STATUS
    # ============================================================

    @commands.command()
    async def status(
        self,
        ctx,
        member: discord.Member,
        channel: discord.TextChannel = None
    ):

        # ========================================================
        # SERVER ONLY
        # ========================================================

        if ctx.guild is None:

            await ctx.send(
                f"{EMOJIS['highlight']} "
                f"This command can only be used in a server."
            )

            return


        # ========================================================
        # CHANNEL PERMISSION
        # ========================================================

        if channel is not None:

            permissions = channel.permissions_for(
                ctx.guild.me
            )

            if not permissions.view_channel:

                await ctx.send(
                    f"{EMOJIS['highlight']} "
                    f"I cannot view {channel.mention}."
                )

                return


            if not permissions.read_message_history:

                await ctx.send(
                    f"{EMOJIS['highlight']} "
                    f"I cannot read message history in "
                    f"{channel.mention}."
                )

                return


        # ========================================================
        # SEND CALCULATING MESSAGE
        # ========================================================

        message = await ctx.send(
            f"{EMOJIS['highlight']} "
            f"Calculating status for **{member}**..."
        )


        # ========================================================
        # STATISTICS
        # ========================================================

        message_count = 0
        image_count = 0
        video_count = 0
        link_count = 0

        first_message = None
        last_message = None


        # ========================================================
        # CHANNEL LIST
        # ========================================================

        if channel is not None:

            channels = [channel]

        else:

            channels = []


            for guild_channel in ctx.guild.text_channels:

                permissions = guild_channel.permissions_for(
                    ctx.guild.me
                )

                if not permissions.view_channel:
                    continue

                if not permissions.read_message_history:
                    continue

                channels.append(
                    guild_channel
                )


        # ========================================================
        # SCAN MESSAGE HISTORY
        # ========================================================

        try:

            for scan_channel in channels:

                try:

                    async for msg in scan_channel.history(
                        limit=None,
                        oldest_first=True
                    ):

                        if msg.author.id != member.id:
                            continue


                        # ------------------------------------------------
                        # MESSAGE COUNT
                        # ------------------------------------------------

                        message_count += 1


                        # ------------------------------------------------
                        # FIRST MESSAGE
                        # ------------------------------------------------

                        if first_message is None:

                            first_message = msg


                        # ------------------------------------------------
                        # LAST MESSAGE
                        # ------------------------------------------------

                        last_message = msg


                        # ------------------------------------------------
                        # ATTACHMENTS
                        # ------------------------------------------------

                        for attachment in msg.attachments:

                            content_type = (
                                attachment.content_type
                                or ""
                            ).lower()


                            filename = (
                                attachment.filename
                                or ""
                            ).lower()


                            # Image
                            if (
                                content_type.startswith("image/")
                                or filename.endswith(
                                    (
                                        ".png",
                                        ".jpg",
                                        ".jpeg",
                                        ".gif",
                                        ".webp",
                                        ".bmp",
                                        ".svg"
                                    )
                                )
                            ):

                                image_count += 1


                            # Video
                            elif (
                                content_type.startswith("video/")
                                or filename.endswith(
                                    (
                                        ".mp4",
                                        ".mov",
                                        ".avi",
                                        ".mkv",
                                        ".webm",
                                        ".flv",
                                        ".wmv"
                                    )
                                )
                            ):

                                video_count += 1


                        # ------------------------------------------------
                        # LINKS
                        # ------------------------------------------------

                        links = URL_PATTERN.findall(
                            msg.content
                        )

                        link_count += len(
                            links
                        )


                except (
                    discord.Forbidden,
                    discord.HTTPException
                ):

                    # Skip channels that cannot be scanned
                    continue


        except discord.HTTPException:

            await message.edit(
                content=(
                    f"{EMOJIS['highlight']} "
                    f"An error occurred while reading "
                    f"the message history."
                )
            )

            return


        # ========================================================
        # DATE FORMAT
        # ========================================================

        if first_message is not None:

            first_message_date = (
                discord.utils.format_dt(
                    first_message.created_at,
                    style="F"
                )
            )

        else:

            first_message_date = "No messages found"


        if last_message is not None:

            last_message_date = (
                discord.utils.format_dt(
                    last_message.created_at,
                    style="F"
                )
            )

        else:

            last_message_date = "No messages found"


        # ========================================================
        # CHANNEL NAME
        # ========================================================

        if channel is not None:

            location = (
                f"Channel: {channel.mention}"
            )

        else:

            location = (
                "Channel: **All accessible channels**"
            )


        # ========================================================
        # FINAL RESPONSE
        # ========================================================

        content = (
            f"# {EMOJIS['highlight']} User Status\n"
            f"\n"
            f"User: {member.mention}\n"
            f"{location}\n"
            f"\n"
            f"💬 Messages: `{message_count:,}`\n"
            f"🖼️ Images: `{image_count:,}`\n"
            f"🎥 Videos: `{video_count:,}`\n"
            f"🔗 Links: `{link_count:,}`\n"
            f"\n"
            f"📅 First Message:\n"
            f"{first_message_date}\n"
            f"\n"
            f"🕐 Last Message:\n"
            f"{last_message_date}"
        )


        # ========================================================
        # EDIT MESSAGE
        # ========================================================

        await message.edit(
            content=content
        )


# ================================================================
# SETUP
# ================================================================

async def setup(bot):

    await bot.add_cog(
        StatusModule(bot)
    )