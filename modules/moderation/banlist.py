from permissions import signed_permission
import math
import discord
from modules.general.emoji import EMOJIS

from discord.ext import commands


class BanListView(discord.ui.View):

    def __init__(self, pages):
        super().__init__(timeout=120)

        self.pages = pages
        self.current_page = 0

        self.update_buttons()


    def update_buttons(self):

        self.previous_button.disabled = (
            self.current_page == 0
        )

        self.next_button.disabled = (
            self.current_page >= len(self.pages) - 1
        )


    @discord.ui.button(
        label="⬅️",
        style=discord.ButtonStyle.secondary
    )
    async def previous_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.current_page -= 1

        self.update_buttons()

        await interaction.response.edit_message(
            content=self.pages[self.current_page],
            view=self
        )


    @discord.ui.button(
        label="➡️",
        style=discord.ButtonStyle.secondary
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.current_page += 1

        self.update_buttons()

        await interaction.response.edit_message(
            content=self.pages[self.current_page],
            view=self
        )


class BanListModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @signed_permission()
    async def banlist(self, ctx):

        bans = [
            ban_entry
            async for ban_entry
            in ctx.guild.bans()
        ]


        if not bans:

            await ctx.send(
                "{EMOJIS['highlight']} 📋 The ban list is empty."
            )

            return


        per_page = 10
        pages = []

        total_pages = math.ceil(
            len(bans) / per_page
        )


        for page in range(total_pages):

            start = page * per_page
            end = start + per_page

            ban_entries = bans[start:end]

            content = (
                f"{EMOJIS['highlight']} 📋 **Ban List — "
                f"Page {page + 1}/{total_pages}**\n\n"
            )


            for index, ban_entry in enumerate(
                ban_entries,
                start=start + 1
            ):

                user = ban_entry.user

                reason = (
                    ban_entry.reason
                    or "No reason provided"
                )

                username = (
                    user.global_name
                    or user.name
                )

                content += (
                    f"{EMOJIS['highlight']} `{index}.` **{username}**\n"
                    f"{EMOJIS['highlight']} 🆔 ID: `{user.id}`\n"
                    f"{EMOJIS['highlight']} 📝 Reason: {reason}\n\n"
                )


            pages.append(content)


        view = BanListView(pages)

        await ctx.send(
            pages[0],
            view=view
        )


async def setup(bot):

    await bot.add_cog(
        BanListModule(bot)
    )