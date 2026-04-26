from __future__ import annotations

import json
import os
from pathlib import Path

import mysql.connector


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_CONFIG_FILE = PROJECT_ROOT / "runtime" / "mysql" / "app_db.json"

DEFAULT_DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "camouflage_app",
    "password": "Camouflage@2026",
    "database": "camouflage_insect_app",
}

_schema_ready = False


def load_db_config() -> dict:
    config = dict(DEFAULT_DB_CONFIG)
    if DB_CONFIG_FILE.exists():
        try:
            config.update(json.loads(DB_CONFIG_FILE.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass

    env_map = {
        "host": os.getenv("CAMOUFLAGE_DB_HOST"),
        "port": os.getenv("CAMOUFLAGE_DB_PORT"),
        "user": os.getenv("CAMOUFLAGE_DB_USER"),
        "password": os.getenv("CAMOUFLAGE_DB_PASSWORD"),
        "database": os.getenv("CAMOUFLAGE_DB_NAME"),
    }

    for key, value in env_map.items():
        if value not in (None, ""):
            config[key] = int(value) if key == "port" else value

    return config


def get_connection() -> mysql.connector.MySQLConnection:
    config = load_db_config()
    return mysql.connector.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        charset="utf8mb4",
        use_unicode=True,
    )


def _table_has_column(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (table_name, column_name),
    )
    return cursor.fetchone()[0] > 0


def _table_has_index(cursor, table_name: str, index_name: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND INDEX_NAME = %s
        """,
        (table_name, index_name),
    )
    return cursor.fetchone()[0] > 0


def ensure_schema() -> None:
    global _schema_ready
    if _schema_ready:
        return

    statements = [
        """
        CREATE TABLE IF NOT EXISTS app_history (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            created_at DATETIME NOT NULL,
            label VARCHAR(191) NOT NULL,
            decision_text VARCHAR(191) NOT NULL,
            upload_name VARCHAR(255) NOT NULL,
            thumbnail_src LONGTEXT NOT NULL
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS app_latest_result (
            cache_key VARCHAR(64) PRIMARY KEY,
            payload LONGTEXT NOT NULL,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS app_analysis_records (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            created_at DATETIME NOT NULL,
            user_id BIGINT NULL,
            class_key VARCHAR(64) NULL,
            label VARCHAR(191) NOT NULL,
            decision_text VARCHAR(191) NOT NULL,
            upload_name VARCHAR(255) NOT NULL,
            thumbnail_src LONGTEXT NOT NULL,
            payload_encoding VARCHAR(32) NOT NULL DEFAULT 'gzip-json',
            result_payload LONGBLOB NOT NULL
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS app_users (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(64) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            display_name VARCHAR(128) NOT NULL,
            role VARCHAR(32) NOT NULL,
            avatar_src LONGTEXT NULL,
            created_at DATETIME NOT NULL,
            last_login_at DATETIME NULL
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS app_posts (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            user_id BIGINT NOT NULL,
            content TEXT NOT NULL,
            image_src LONGTEXT NULL,
            tag_label VARCHAR(64) NULL,
            created_at DATETIME NOT NULL
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """,
        """
        CREATE TABLE IF NOT EXISTS app_user_follows (
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            follower_user_id BIGINT NOT NULL,
            followee_user_id BIGINT NOT NULL,
            created_at DATETIME NOT NULL,
            UNIQUE KEY uniq_follower_followee (follower_user_id, followee_user_id)
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """,
    ]

    connection = get_connection()
    cursor = connection.cursor()
    try:
        for statement in statements:
            cursor.execute(statement)

        if not _table_has_column(cursor, "app_history", "user_id"):
            cursor.execute("ALTER TABLE app_history ADD COLUMN user_id BIGINT NULL AFTER id")
            cursor.execute("CREATE INDEX idx_app_history_user_id ON app_history (user_id)")

        if not _table_has_column(cursor, "app_latest_result", "user_id"):
            cursor.execute("ALTER TABLE app_latest_result ADD COLUMN user_id BIGINT NULL AFTER cache_key")
            cursor.execute("CREATE INDEX idx_app_latest_result_user_id ON app_latest_result (user_id)")

        if not _table_has_column(cursor, "app_users", "avatar_src"):
            cursor.execute("ALTER TABLE app_users ADD COLUMN avatar_src LONGTEXT NULL AFTER role")

        if not _table_has_index(cursor, "app_analysis_records", "idx_app_analysis_records_user_created"):
            try:
                cursor.execute(
                    """
                    CREATE INDEX idx_app_analysis_records_user_created
                    ON app_analysis_records (user_id, id)
                    """
                )
            except mysql.connector.Error as exc:
                if exc.errno != 1061:
                    raise

        if not _table_has_index(cursor, "app_posts", "idx_app_posts_user_created"):
            try:
                cursor.execute(
                    """
                    CREATE INDEX idx_app_posts_user_created
                    ON app_posts (user_id, id)
                    """
                )
            except mysql.connector.Error as exc:
                if exc.errno != 1061:
                    raise

        if not _table_has_index(cursor, "app_user_follows", "idx_app_user_follows_followee"):
            try:
                cursor.execute(
                    """
                    CREATE INDEX idx_app_user_follows_followee
                    ON app_user_follows (followee_user_id)
                    """
                )
            except mysql.connector.Error as exc:
                if exc.errno != 1061:
                    raise

        connection.commit()
        _schema_ready = True
    finally:
        cursor.close()
        connection.close()
