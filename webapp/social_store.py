from __future__ import annotations

from datetime import datetime

from webapp.db import ensure_schema, get_connection


def _user_preview(row: dict | None) -> dict | None:
    if not row:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "role": row.get("role", "user"),
        "avatar_src": row.get("avatar_src"),
    }


def create_post(user_id: int, content: str, image_src: str | None = None, tag_label: str | None = None) -> int:
    ensure_schema()
    text = (content or "").strip()
    if len(text) < 2:
        if image_src:
            text = "我也发了一张观察图。"
        else:
            raise ValueError("动态内容至少需要 2 个字，或者上传一张图片。")

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO app_posts (user_id, content, image_src, tag_label, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, text, image_src or None, (tag_label or "").strip() or None, datetime.now()),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        cursor.close()
        connection.close()


def delete_post(post_id: int, user_id: int | None = None, allow_any: bool = False) -> None:
    ensure_schema()
    if not allow_any and not user_id:
        raise ValueError("当前账号没有删除这条动态的权限。")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        if allow_any:
            cursor.execute("SELECT id FROM app_posts WHERE id = %s LIMIT 1", (post_id,))
        else:
            cursor.execute(
                "SELECT id FROM app_posts WHERE id = %s AND user_id = %s LIMIT 1",
                (post_id, user_id),
            )
        if not cursor.fetchone():
            raise ValueError("这条动态不存在，或当前账号没有删除权限。")

        cursor.execute("DELETE FROM app_posts WHERE id = %s", (post_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def list_feed_posts(viewer_user_id: int | None = None, limit: int = 20) -> list[dict]:
    ensure_schema()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                p.id,
                p.content,
                p.image_src,
                p.tag_label,
                p.created_at,
                u.id AS user_id,
                u.username,
                u.display_name,
                u.role,
                u.avatar_src
            FROM app_posts p
            JOIN app_users u ON u.id = p.user_id
            ORDER BY p.id DESC
            LIMIT %s
            """,
            (limit,),
        )
        posts = []
        for row in cursor.fetchall():
            posts.append(
                {
                    "id": row["id"],
                    "content": row["content"],
                    "image_src": row["image_src"],
                    "tag_label": row["tag_label"] or "",
                    "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M"),
                    "author": _user_preview(row),
                    "is_self": bool(viewer_user_id and row["user_id"] == viewer_user_id),
                }
            )
        return posts
    finally:
        cursor.close()
        connection.close()


def list_user_posts(user_id: int, limit: int = 20) -> list[dict]:
    ensure_schema()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                p.id,
                p.content,
                p.image_src,
                p.tag_label,
                p.created_at,
                u.id AS user_id,
                u.username,
                u.display_name,
                u.role,
                u.avatar_src
            FROM app_posts p
            JOIN app_users u ON u.id = p.user_id
            WHERE p.user_id = %s
            ORDER BY p.id DESC
            LIMIT %s
            """,
            (user_id, limit),
        )
        posts = []
        for row in cursor.fetchall():
            posts.append(
                {
                    "id": row["id"],
                    "content": row["content"],
                    "image_src": row["image_src"],
                    "tag_label": row["tag_label"] or "",
                    "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M"),
                    "author": _user_preview(row),
                    "is_self": True,
                }
            )
        return posts
    finally:
        cursor.close()
        connection.close()


def search_friend_candidates(keyword: str, current_user_id: int, limit: int = 12) -> list[dict]:
    ensure_schema()
    query = (keyword or "").strip()
    if len(query) < 1:
        return []

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        like = f"%{query}%"
        cursor.execute(
            """
            SELECT
                u.id,
                u.username,
                u.display_name,
                u.role,
                u.avatar_src,
                EXISTS(
                    SELECT 1
                    FROM app_user_follows f
                    WHERE f.follower_user_id = %s
                      AND f.followee_user_id = u.id
                ) AS is_following
            FROM app_users u
            WHERE u.id <> %s
              AND u.role = 'user'
              AND (u.username LIKE %s OR u.display_name LIKE %s)
            ORDER BY u.id DESC
            LIMIT %s
            """,
            (current_user_id, current_user_id, like, like, limit),
        )
        results = []
        for row in cursor.fetchall():
            user = _user_preview(row) or {}
            user["is_following"] = bool(row["is_following"])
            results.append(user)
        return results
    finally:
        cursor.close()
        connection.close()


def list_following(current_user_id: int, limit: int = 30) -> list[dict]:
    ensure_schema()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                u.id,
                u.username,
                u.display_name,
                u.role,
                u.avatar_src,
                f.created_at
            FROM app_user_follows f
            JOIN app_users u ON u.id = f.followee_user_id
            WHERE f.follower_user_id = %s
            ORDER BY f.id DESC
            LIMIT %s
            """,
            (current_user_id, limit),
        )
        results = []
        for row in cursor.fetchall():
            user = _user_preview(row) or {}
            user["followed_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M")
            results.append(user)
        return results
    finally:
        cursor.close()
        connection.close()


def follow_user(current_user_id: int, target_user_id: int) -> None:
    ensure_schema()
    if current_user_id == target_user_id:
        raise ValueError("不能关注自己。")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, role FROM app_users WHERE id = %s LIMIT 1",
            (target_user_id,),
        )
        target = cursor.fetchone()
        if not target or target["role"] != "user":
            raise ValueError("目标用户不存在或不可关注。")

        cursor.execute(
            """
            INSERT INTO app_user_follows (follower_user_id, followee_user_id, created_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE created_at = created_at
            """,
            (current_user_id, target_user_id, datetime.now()),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def count_posts() -> int:
    ensure_schema()
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM app_posts")
        return int(cursor.fetchone()[0])
    finally:
        cursor.close()
        connection.close()


def count_follow_relations() -> int:
    ensure_schema()
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM app_user_follows")
        return int(cursor.fetchone()[0])
    finally:
        cursor.close()
        connection.close()
