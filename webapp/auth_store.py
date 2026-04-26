from __future__ import annotations

from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from webapp.db import ensure_schema, get_connection


DEFAULT_USERS = [
    {
        "username": "admin",
        "password": "CamouflageAdmin@2026",
        "display_name": "系统管理员",
        "role": "admin",
    },
    {
        "username": "observer",
        "password": "CamouflageUser@2026",
        "display_name": "观察记录员",
        "role": "user",
    },
    {
        "username": "forest_watch",
        "password": "ForestWatch@2026",
        "display_name": "林下观察站",
        "role": "user",
    },
    {
        "username": "wetland_patrol",
        "password": "WetlandPatrol@2026",
        "display_name": "湿地巡查组",
        "role": "user",
    },
    {
        "username": "edge_recorder",
        "password": "EdgeRecorder@2026",
        "display_name": "林缘记录员",
        "role": "user",
    },
    {
        "username": "flower_monitor",
        "password": "FlowerMonitor@2026",
        "display_name": "花灌木监测点",
        "role": "user",
    },
    {
        "username": "night_watch",
        "password": "NightWatch@2026",
        "display_name": "夜间观察队",
        "role": "user",
    },
]


def ensure_default_users() -> None:
    ensure_schema()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM app_users")
        if int(cursor.fetchone()["total"]) > 0:
            return

        for item in DEFAULT_USERS:
            cursor.execute(
                """
                INSERT INTO app_users (username, password_hash, display_name, role, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    item["username"],
                    generate_password_hash(item["password"]),
                    item["display_name"],
                    item["role"],
                    datetime.now(),
                ),
            )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def _sanitize_user(row: dict | None) -> dict | None:
    if not row:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "role": row["role"],
        "avatar_src": row.get("avatar_src"),
        "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M") if row.get("created_at") else "",
        "last_login_at": row["last_login_at"].strftime("%Y-%m-%d %H:%M") if row.get("last_login_at") else "首次登录前",
    }


def get_user_by_id(user_id: int | None) -> dict | None:
    if not user_id:
        return None

    ensure_default_users()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, username, display_name, role, avatar_src, created_at, last_login_at
            FROM app_users
            WHERE id = %s
            LIMIT 1
            """,
            (user_id,),
        )
        return _sanitize_user(cursor.fetchone())
    finally:
        cursor.close()
        connection.close()


def authenticate_user(username: str, password: str) -> dict | None:
    ensure_default_users()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, username, password_hash, display_name, role, avatar_src, created_at, last_login_at
            FROM app_users
            WHERE username = %s
            LIMIT 1
            """,
            (username.strip(),),
        )
        row = cursor.fetchone()
        if not row or not check_password_hash(row["password_hash"], password):
            return None

        cursor.execute("UPDATE app_users SET last_login_at = %s WHERE id = %s", (datetime.now(), row["id"]))
        connection.commit()
        row["last_login_at"] = datetime.now()
        return _sanitize_user(row)
    finally:
        cursor.close()
        connection.close()


def list_users(limit: int = 50) -> list[dict]:
    ensure_default_users()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, username, display_name, role, avatar_src, created_at, last_login_at
            FROM app_users
            ORDER BY id ASC
            LIMIT %s
            """,
            (limit,),
        )
        return [_sanitize_user(row) for row in cursor.fetchall()]
    finally:
        cursor.close()
        connection.close()


def create_user(username: str, password: str, display_name: str, role: str = "user") -> dict:
    ensure_default_users()
    username = username.strip()
    display_name = display_name.strip() or username
    role = "admin" if role == "admin" else "user"

    if len(username) < 3:
        raise ValueError("用户名至少需要 3 个字符。")
    if len(password) < 6:
        raise ValueError("密码至少需要 6 个字符。")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM app_users WHERE username = %s LIMIT 1", (username,))
        if cursor.fetchone():
            raise ValueError("这个用户名已经存在，请更换一个。")

        cursor.execute(
            """
            INSERT INTO app_users (username, password_hash, display_name, role, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                username,
                generate_password_hash(password),
                display_name,
                role,
                datetime.now(),
            ),
        )
        connection.commit()
        return get_user_by_id(cursor.lastrowid) or {}
    finally:
        cursor.close()
        connection.close()


def count_users() -> int:
    ensure_default_users()
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM app_users")
        return int(cursor.fetchone()[0])
    finally:
        cursor.close()
        connection.close()


def update_user_avatar(user_id: int, avatar_src: str | None) -> dict | None:
    ensure_default_users()
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE app_users SET avatar_src = %s WHERE id = %s", (avatar_src, user_id))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    return get_user_by_id(user_id)


def delete_user_account(target_user_id: int) -> None:
    ensure_default_users()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, role FROM app_users WHERE id = %s LIMIT 1",
            (target_user_id,),
        )
        target = cursor.fetchone()
        if not target:
            raise ValueError("目标账号不存在。")

        if target["role"] == "admin":
            cursor.execute("SELECT COUNT(*) AS total FROM app_users WHERE role = 'admin'")
            admin_total = int(cursor.fetchone()["total"])
            if admin_total <= 1:
                raise ValueError("平台至少需要保留一个管理员账号。")

        cursor.execute(
            """
            DELETE FROM app_user_follows
            WHERE follower_user_id = %s OR followee_user_id = %s
            """,
            (target_user_id, target_user_id),
        )
        cursor.execute("DELETE FROM app_posts WHERE user_id = %s", (target_user_id,))
        cursor.execute("DELETE FROM app_analysis_records WHERE user_id = %s", (target_user_id,))
        cursor.execute("DELETE FROM app_latest_result WHERE user_id = %s OR cache_key = %s", (target_user_id, f"user:{target_user_id}"))
        cursor.execute("DELETE FROM app_history WHERE user_id = %s", (target_user_id,))
        cursor.execute("DELETE FROM app_users WHERE id = %s", (target_user_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
