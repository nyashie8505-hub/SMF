import os

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


# ================================================================
# LOAD ENVIRONMENT
# ================================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ================================================================
# DATABASE CONNECTION
# ================================================================

def get_connection():

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set."
        )

    connection = psycopg2.connect(
        DATABASE_URL,
        connect_timeout=10
    )

    return connection


# ================================================================
# INITIALIZE DATABASE
# ================================================================

def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    # ============================================================
    # WARNINGS
    # ============================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS warnings (

            id BIGSERIAL PRIMARY KEY,

            guild_id BIGINT NOT NULL,

            user_id BIGINT NOT NULL,

            moderator_id BIGINT NOT NULL,

            reason TEXT NOT NULL,

            created_at BIGINT NOT NULL

        )
        """
    )

    # ============================================================
    # COMMAND PERMISSIONS
    # ============================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS command_permissions (

            guild_id BIGINT NOT NULL,

            role_id BIGINT NOT NULL,

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

            guild_id BIGINT PRIMARY KEY,

            role_id BIGINT NOT NULL

        )
        """
    )

    # ============================================================
    # MODLOG CHANNELS
    # ============================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS modlog_channels (

            guild_id BIGINT NOT NULL,

            channel_id BIGINT NOT NULL,

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

            guild_id BIGINT NOT NULL,

            channel_id BIGINT NOT NULL,

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

    cursor.close()
    connection.close()


# ================================================================
# BACKWARDS COMPATIBILITY
# ================================================================

def initialize_database():

    init_database()


# ================================================================
# OWNER ROLE
# ================================================================

def get_owner_role(guild_id):

    connection = get_connection()

    cursor = connection.cursor(
        cursor_factory=RealDictCursor
    )

    cursor.execute(
        """
        SELECT role_id

        FROM owner_roles

        WHERE guild_id = %s
        """,
        (
            guild_id,
        )
    )

    row = cursor.fetchone()

    cursor.close()
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

        VALUES (%s, %s)

        ON CONFLICT (guild_id)

        DO UPDATE SET
            role_id = EXCLUDED.role_id
        """,
        (
            guild_id,
            role_id,
        )
    )

    connection.commit()

    cursor.close()
    connection.close()


# ================================================================
# MODLOG CHANNELS
# ================================================================

def get_modlog_channels(guild_id):

    connection = get_connection()

    cursor = connection.cursor(
        cursor_factory=RealDictCursor
    )

    cursor.execute(
        """
        SELECT
            guild_id,
            channel_id

        FROM modlog_channels

        WHERE guild_id = %s

        ORDER BY channel_id ASC
        """,
        (
            guild_id,
        )
    )

    rows = cursor.fetchall()

    cursor.close()
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

        WHERE guild_id = %s

        AND channel_id = %s

        LIMIT 1
        """,
        (
            guild_id,
            channel_id,
        )
    )

    result = cursor.fetchone()

    cursor.close()
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
        INSERT INTO modlog_channels (
            guild_id,
            channel_id
        )

        VALUES (%s, %s)

        ON CONFLICT (
            guild_id,
            channel_id
        )

        DO NOTHING
        """,
        (
            guild_id,
            channel_id,
        )
    )

    connection.commit()

    cursor.close()
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

        WHERE guild_id = %s

        AND channel_id = %s
        """,
        (
            guild_id,
            channel_id,
        )
    )

    connection.commit()

    cursor.close()
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

        WHERE guild_id = %s

        AND channel_id = %s

        AND command_name = %s

        LIMIT 1
        """,
        (
            guild_id,
            channel_id,
            command_name,
        )
    )

    result = cursor.fetchone()

    cursor.close()
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
        INSERT INTO modlog_disabled_commands (
            guild_id,
            channel_id,
            command_name
        )

        VALUES (%s, %s, %s)

        ON CONFLICT (
            guild_id,
            channel_id,
            command_name
        )

        DO NOTHING
        """,
        (
            guild_id,
            channel_id,
            command_name,
        )
    )

    connection.commit()

    cursor.close()
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

        WHERE guild_id = %s

        AND channel_id = %s

        AND command_name = %s
        """,
        (
            guild_id,
            channel_id,
            command_name,
        )
    )

    connection.commit()

    cursor.close()
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

        WHERE guild_id = %s

        AND channel_id = %s
        """,
        (
            guild_id,
            channel_id,
        )
    )

    connection.commit()

    cursor.close()
    connection.close()


# ================================================================
# AUTO INITIALIZATION
# ================================================================

init_database()

