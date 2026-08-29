import json
import os

import discord

from discord.ext import commands


# ================================================================
# CONFIGURATION
# ================================================================

PATCH_FILE = "data/patch_notes.json"

# ================================================================
# PATCH UPDATE OWNER
# ================================================================


PATCH_OWNER_ID = 1263317841902440540


# ================================================================
# PATCH NOTE STORAGE
# ================================================================

def ensure_patch_file():

    os.makedirs(
        "data",
        exist_ok=True
    )

    if not os.path.exists(PATCH_FILE):

        with open(
            PATCH_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [],
                file,
                ensure_ascii=False,
                indent=4
            )


def load_patches():

    ensure_patch_file()

    try:

        with open(
            PATCH_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError):

        return []


def save_patches(patches):

    ensure_patch_file()

    with open(
        PATCH_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            patches,
            file,
            ensure_ascii=False,
            indent=4
        )


# ================================================================
# PATCH EMBED
# ================================================================

def create_patch_embed(
    patches,
    page
):

    patch = patches[page]

    embed = discord.Embed(
        title=f"📦 {patch['title']}",
        description=patch["content"],
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="📌 Note",
        value=patch["note"],
        inline=False
    )

    embed.set_footer(
        text=(
            f"S.M.FAPP Patch Notes • "
            f"{page + 1}/{len(patches)}"
        )
    )

    return embed


# ================================================================
# PATCH NOTE VIEW
# ================================================================

class PatchNoteView(discord.ui.View):

    def __init__(
        self,
        patches,
        current_page=0
    ):

        super().__init__(
            timeout=300
        )

        self.patches = patches
        self.current_page = current_page

        self.update_buttons()


    def update_buttons(self):

        self.previous_button.disabled = (
            self.current_page <= 0
        )

        self.next_button.disabled = (
            self.current_page >= len(self.patches) - 1
        )


    # ============================================================
    # PREVIOUS
    # ============================================================

    @discord.ui.button(
        label="◀",
        style=discord.ButtonStyle.secondary
    )
    async def previous_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if self.current_page > 0:

            self.current_page -= 1

        self.update_buttons()

        embed = create_patch_embed(
            self.patches,
            self.current_page
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


    # ============================================================
    # NEXT
    # ============================================================

    @discord.ui.button(
        label="▶",
        style=discord.ButtonStyle.secondary
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if self.current_page < len(self.patches) - 1:

            self.current_page += 1

        self.update_buttons()

        embed = create_patch_embed(
            self.patches,
            self.current_page
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


# ================================================================
# PATCH NOTE MODULE
# ================================================================

class PatchNoteModule(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot


    # ============================================================
    # DUPN
    # ============================================================

    @commands.command(
        name="pn",
        aliases=[
            "patch",
            "patchnotes"
        ]
    )
    async def patch_notes(
        self,
        ctx
    ):

        patches = load_patches()

        if not patches:

            await ctx.send(
                "📦 There are currently no Patch Notes."
            )

            return


        # Mới nhất nằm cuối danh sách

        current_page = len(patches) - 1

        embed = create_patch_embed(
            patches,
            current_page
        )

        view = PatchNoteView(
            patches,
            current_page
        )

        await ctx.send(
            embed=embed,
            view=view
        )


    # ============================================================
    # DUPATCHUP
    # ============================================================

    @commands.command(
        name="patchup"
    )
    async def patch_update(
        self,
        ctx,
        *,
        update: str
    ):

        # ========================================================
        # CHECK OWNER ID
        # ========================================================

        if ctx.author.id != PATCH_OWNER_ID:

            await ctx.send(
                "❌ You are not authorized to create Patch Updates."
            )

            return


        # ========================================================
        # PARSE UPDATE
        # ========================================================

        parts = [
            part.strip()
            for part in update.split("/")
        ]


        if len(parts) != 3:

            await ctx.send(
                "❌ Invalid format.\n\n"
                "Use:\n"
                "`dupatchup TITLE / CONTENT / NOTE`"
            )

            return


        title = parts[0]
        content = parts[1]
        note = parts[2]


        if not title:

            await ctx.send(
                "❌ The title cannot be empty."
            )

            return


        if not content:

            await ctx.send(
                "❌ The content cannot be empty."
            )

            return


        if not note:

            await ctx.send(
                "❌ The note cannot be empty."
            )

            return


        # ========================================================
        # SAVE UPDATE
        # ========================================================

        patches = load_patches()

        patches.append(
            {
                "title": title,
                "content": content,
                "note": note
            }
        )

        save_patches(
            patches
        )


        # ========================================================
        # SEND CONFIRMATION
        # ========================================================

        embed = discord.Embed(
            title=f"📦 {title}",
            description=content,
            color=discord.Color.green()
        )

        embed.add_field(
            name="📌 Note",
            value=note,
            inline=False
        )

        embed.set_footer(
            text="S.M.FAPP • Patch Update"
        )

        await ctx.send(
            embed=embed
        )


# ================================================================
# SETUP
# ================================================================

async def setup(bot):

    await bot.add_cog(
        PatchNoteModule(bot)
    )

