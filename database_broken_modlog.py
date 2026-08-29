import os
import sqlite3


# ================================================================
# DATABASE CONFIGURATION
# ================================================================

DATABASE = "data/smf.db"


# ================================================================
# GET DATABASE CONNECTION
# ================================================================

def get_connection():

    os.makedirs(
        "data",
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    return connection


# ================================================================
# INITIALIZE DATABASE
# ================================================================

def init_database():

    os.makedirs(
        "data",
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()

    # ============================================================
    # WARNINGS
    # ============================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS warnings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            guild_id INTEGER NOT NULL,

            user_id INTEGER NOT NULL,

            moderator_id INTEGER NOT NULL,

            reason TEXT NOT NULL,

            created_at INTEGER NOT NULL

        )
        """
    )

    # ============================================================
    # COMMAND PERMISSIONS
    # ============================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS command_permissions (

            guild_id INTEGER NOT NULL,

            role_id INTEGER NOT NULL,

            command_name TEXT NOT NULL,

            PRIMARY KEY (
                guild_id,
                role_id,
                command_name
            )

        )
        """
    )

    # ============================================================
    # OWNER ROLES
    # ============================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS owner_roles (

            guild_id INTEGER PRIMARY KEY,

            role_id INTEGER NOT NULL

        )
        """
    )

    # ============================================================
    # MODLOG CHANNELS
    # ============================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS modlog_channels (

            guild_id INTEGER NOT NULL,

            channel_id INTEGER NOT NULL,

            PRIMARY KEY (
                guild_id,
                channel_id
            )

        )
        """
    )

    # ============================================================
    # DISABLED MODLOG COMMANDS
    # ============================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS modlog_disabled_commands (

            guild_id INTEGER NOT NULL,

            channel_id INTEGER NOT NULL,

            command_name TEXT NOT NULL,

            PRIMARY KEY (
                guild_id,
                channel_id,
                command_name
            )

        )
        """
    )

    connection.commit()

    connection.close()


# ================================================================
# BACKWARDS COMPATIBILITY
# ================================================================
#
# Some existing modules use initialize_database().
#
# Keep it available so those modules continue working.
#

def initialize_database():

    init_database()


# ================================================================
# OWNER ROLE
# ================================================================

def get_owner_role(guild_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT role_id

        FROM owner_roles

        WHERE guild_id = ?
        """,
        (
            guild_id,
        )
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return row["role_id"]


# ================================================================
# SET OWNER ROLE
# ================================================================

def set_owner_role(
    guild_id,
    role_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO owner_roles (
            guild_id,
            role_id
        )

        VALUES (?, ?)

        ON CONFLICT(guild_id)

        DO UPDATE SET
            role_id = excluded.role_id
        """,
        (
            guild_id,
            role_id,
        )
    )

    connection.commit()

    connection.close()


# ================================================================
# MODLOG CHANNELS
# ================================================================

def get_modlog_channels(guild_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            guild_id,
            channel_id

        FROM modlog_channels

        WHERE guild_id = ?

        ORDER BY channel_id ASC
        """,
        (
            guild_id,
        )
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


# ================================================================
# CHECK MODLOG CHANNEL
# ================================================================

def is_modlog_channel(
    guild_id,
    channel_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 1

        FROM modlog_channels

        WHERE guild_id = ?

        AND channel_id = ?

        LIMIT 1
        """,
        (
            guild_id,
            channel_id,
        )
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


# ================================================================
# ADD MODLOG CHANNEL
# ================================================================

def add_modlog_channel(
    guild_id,
    channel_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO modlog_channels (

            guild_id,
            channel_id

        )

        VALUES (?, ?)
        """,
        (
            guild_id,
            channel_id,
        )
    )

    connection.commit()

    connection.close()


# ================================================================
# REMOVE MODLOG CHANNEL
# ================================================================

def remove_modlog_channel(
    guild_id,
    channel_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM modlog_channels

        WHERE guild_id = ?

        AND channel_id = ?
        """,
        (
            guild_id,
            channel_id,
        )
    )

    connection.commit()

    connection.close()


# ================================================================
# CHECK DISABLED MODLOG COMMAND
# ================================================================

def is_modlog_command_disabled(
    guild_id,
    channel_id,
    command_name
):

    command_name = str(
        command_name
    ).lower()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 1

        FROM modlog_disabled_commands

        WHERE guild_id = ?

        AND channel_id = ?

        AND command_name = ?

        LIMIT 1
        """,
        (
            guild_id,
            channel_id,
            command_name,
        )
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


# ================================================================
# DISABLE MODLOG COMMAND
# ================================================================

def disable_modlog_command(
    guild_id,
    channel_id,
    command_name
):

    command_name = str(
        command_name
    ).lower()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO modlog_disabled_commands (

            guild_id,
            channel_id,
            command_name

        )

        VALUES (?, ?, ?)
        """,
        (
            guild_id,
            channel_id,
            command_name,
        )
    )

    connection.commit()

    connection.close()


# ================================================================
# ENABLE MODLOG COMMAND
# ================================================================

def enable_modlog_command(
    guild_id,
    channel_id,
    command_name
):

    command_name = str(
        command_name
    ).lower()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM modlog_disabled_commands

        WHERE guild_id = ?

        AND channel_id = ?

        AND command_name = ?
        """,
        (
            guild_id,
            channel_id,
            command_name,
        )
    )

    connection.commit()

    connection.close()


# ================================================================
# CLEAR DISABLED MODLOG COMMANDS
# ================================================================

def clear_disabled_modlog_commands(
    guild_id,
    channel_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM modlog_disabled_commands

        WHERE guild_id = ?

        AND channel_id = ?
        """,
        (
            guild_id,
            channel_id,
        )
    )

    connection.commit()

    connection.close()


# ================================================================
# AUTO INITIALIZATION
# ================================================================

init_database()