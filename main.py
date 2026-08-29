import os
import asyncio

import discord

from discord.ext import commands

from config import TOKEN, PREFIX
from database import init_database


# ================================================================
# DISCORD INTENTS
# ================================================================

intents = discord.Intents.default()

intents.message_content = True
intents.members = True


# ================================================================
# BOT
# ================================================================

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


# ================================================================
# READY
# ================================================================

@bot.event
async def on_ready():

    print("=" * 40)
    print(
        f"[ONLINE] Logged in as {bot.user}"
    )
    print(
        f"[ID] {bot.user.id}"
    )
    print("=" * 40)

@bot.event
async def on_command_error(ctx, error):

    print(
        f"[COMMAND ERROR] "
        f"{ctx.command}: "
        f"{type(error).__name__}: "
        f"{error}"
    )

    # Ignore unknown commands
    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return




# ================================================================
# LOAD MODULES
# ================================================================

async def load_modules():

    for root, dirs, files in os.walk(
        "modules"
    ):

        for file in files:

            # ----------------------------------------------------
            # Only Python files
            # ----------------------------------------------------

            if not file.endswith(".py"):
                continue


            # ----------------------------------------------------
            # Ignore package/helper files
            # ----------------------------------------------------

            if file in [
                "__init__.py",
                "emoji.py"
            ]:
                continue


            # ----------------------------------------------------
            # Convert file path to module path
            # ----------------------------------------------------

            file_path = os.path.join(
                root,
                file
            )


            module_path = (
                file_path[:-3]
                .replace(
                    os.sep,
                    "."
                )
            )


            # ----------------------------------------------------
            # Load extension
            # ----------------------------------------------------

            try:

                await bot.load_extension(
                    module_path
                )

                print(
                    f"[OK] Loaded: "
                    f"{module_path}"
                )


            except Exception as error:

                print(
                    f"[ERROR] Failed to load: "
                    f"{module_path}"
                )

                print(
                    f"{type(error).__name__}: "
                    f"{error}"
                )


# ================================================================
# MAIN
# ================================================================

async def main():

    # ------------------------------------------------------------
    # Check token
    # ------------------------------------------------------------

    if not TOKEN:

        print(
            "[ERROR] DISCORD_TOKEN was not found."
        )

        return


    # ------------------------------------------------------------
    # Initialize database
    # ------------------------------------------------------------

    try:

        init_database()

        print(
            "[OK] Database initialized."
        )

    except Exception as error:

        print(
            "[ERROR] Database initialization failed."
        )

        print(
            f"{type(error).__name__}: "
            f"{error}"
        )

        return


    # ------------------------------------------------------------
    # Start bot
    # ------------------------------------------------------------

    async with bot:

        # Load all modules
        await load_modules()

        # Start Discord connection
        await bot.start(
            TOKEN
        )


# ================================================================
# ENTRY POINT
# ================================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        print(
            "\n[OFFLINE] Bot stopped."
        )