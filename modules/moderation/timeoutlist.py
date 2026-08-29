from permissions import signed_permission
import math
import discord

from discord.ext import commands


class TimeoutListView(discord.ui.View):

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


class TimeoutListModule(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @signed_permission()
    async def timeoutlist(self, ctx):

        timed_out_members = [

            member

            for member in ctx.guild.members

            if member.is_timed_out()

        ]


        if not timed_out_members:

            await ctx.send(
                "🔻 📋 There are no timed out members."
            )

            return


        per_page = 10

        pages = []

        total_pages = math.ceil(
            len(timed_out_members) / per_page
        )


        for page in range(total_pages):

            start = page * per_page

            end = start + per_page

            members = timed_out_members[start:end]


            content = (
                f"🔻 📋 **Timeout List — "
                f"Page {page + 1}/{total_pages}**\n\n"
            )


            for index, member in enumerate(
                members,
                start=start + 1
            ):

                timeout_until = member.timed_out_until

                timestamp = int(
                    timeout_until.timestamp()
                )


                content += (
                    f"🔻 `{index}.` {member.mention}\n"
                    f"🔻 ⏱️ Until: <t:{timestamp}:R>\n\n"
                )


            pages.append(content)


        view = TimeoutListView(pages)

        await ctx.send(
            pages[0],
            view=view
        )


async def setup(bot):

    await bot.add_cog(
        TimeoutListModule(bot)
    )