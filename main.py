import os
import asyncio

import discord

from discord.ext import commands

from config import TOKEN, PREFIX
from database import init_database


intents = discord.Intents.default()

intents.message_content = True
intents.members = True


bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


@bot.event
async def on_ready():

    print("=" * 40)
    print(f"[ONLINE] Logged in as {bot.user}")
    print(f"[ID] {bot.user.id}")
    print("=" * 40)


async def load_modules():

    for root, dirs, files in os.walk("modules"):

        for file in files:

            if not file.endswith(".py"):
                continue


            if file in [
                "__init__.py",
                "emoji.py"
            ]:
                continue


            file_path = os.path.join(
                root,
                file
            )


            module_path = (
                file_path[:-3]
                .replace(os.sep, ".")
            )


            try:

                await bot.load_extension(
                    module_path
                )

                print(
                    f"[OK] Loaded: {module_path}"
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


async def main():

    if not TOKEN:

        print(
            "[ERROR] DISCORD_TOKEN was not found."
        )

        return


    init_database()


    async with bot:

        await load_modules()

        await bot.start(TOKEN)


if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print(
            "\n[OFFLINE] Bot stopped."
        )