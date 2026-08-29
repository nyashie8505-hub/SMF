import os
import re


FOLDER = "modules/moderation"

SKIP_FILES = [
    "sign.py",
    "unsign.py",
    "__init__.py"
]


for filename in os.listdir(FOLDER):

    if not filename.endswith(".py"):
        continue

    if filename in SKIP_FILES:
        continue


    filepath = os.path.join(
        FOLDER,
        filename
    )


    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as file:

        content = file.read()


    # Replace Discord user permission checks
    new_content = re.sub(
        r'@commands\.has_permissions\([^)]*\)',
        '@signed_permission()',
        content
    )


    # Add the import if the file was changed
    if new_content != content:

        if (
            "from permissions import signed_permission"
            not in new_content
        ):

            new_content = (
                "from permissions import signed_permission\n"
                + new_content
            )


        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                new_content
            )


        print(
            f"[UPDATED] {filename}"
        )

    else:

        print(
            f"[SKIPPED] {filename}"
        )


print("\nDone.")