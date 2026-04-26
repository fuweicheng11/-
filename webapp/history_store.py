from __future__ import annotations

import json
import gzip
from datetime import datetime

from webapp.db import ensure_schema, get_connection


MAX_HISTORY = 5
LATEST_RESULT_KEY = "latest"


def _cache_key_for_user(user_id: int | None) -> str:
    return f"user:{user_id}" if user_id else LATEST_RESULT_KEY


def _encode_payload(result: dict) -> bytes:
    payload = json.dumps(result, ensure_ascii=False).encode("utf-8")
    return gzip.compress(payload)


def _decode_payload(payload: bytes | bytearray | memoryview, encoding: str) -> dict:
    raw = bytes(payload)
    if encoding == "gzip-json":
        return json.loads(gzip.decompress(raw).decode("utf-8"))
    return json.loads(raw.decode("utf-8"))


def _history_filter(user_id: int | None) -> tuple[str, tuple]:
    if user_id:
        return "user_id = %s", (user_id,)
    return "user_id IS NULL", ()


def load_analysis_record(record_id: int, user_id: int | None = None, allow_any: bool = False) -> dict | None:
    ensure_schema()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        if allow_any:
            cursor.execute(
                """
                SELECT id, result_payload, payload_encoding
                FROM app_analysis_records
                WHERE id = %s
                LIMIT 1
                """,
                (record_id,),
            )
        elif user_id:
            cursor.execute(
                """
                SELECT id, result_payload, payload_encoding
                FROM app_analysis_records
                WHERE id = %s AND user_id = %s
                LIMIT 1
                """,
                (record_id, user_id),
            )
        else:
            cursor.execute(
                """
                SELECT id, result_payload, payload_encoding
                FROM app_analysis_records
                WHERE id = %s AND user_id IS NULL
                LIMIT 1
                """,
                (record_id,),
            )

        row = cursor.fetchone()
        if not row:
            return None

        result = _decode_payload(row["result_payload"], row["payload_encoding"])
        result["record_id"] = row["id"]
        return result
    finally:
        cursor.close()
        connection.close()


def load_history(limit: int = MAX_HISTORY, user_id: int | None = None) -> list[dict]:
    ensure_schema()
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        where_clause, params = _history_filter(user_id)
        cursor.execute(
            f"""
            SELECT id, created_at, label, decision_text, upload_name, thumbnail_src
            FROM app_analysis_records
            WHERE {where_clause}
            ORDER BY id DESC
            LIMIT %s
            """,
            (*params, limit),
        )
        rows = cursor.fetchall()
        history = []
        for row in rows:
            history.append(
                {
                    "record_id": row["id"],
                    "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M"),
                    "label": row["label"],
                    "decision_text": row["decision_text"],
                    "upload_name": row["upload_name"],
                    "thumbnail_src": row["thumbnail_src"],
                }
            )
        return history
    finally:
        cursor.close()
        connection.close()


def count_history_records() -> int:
    ensure_schema()
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM app_analysis_records")
        return int(cursor.fetchone()[0])
    finally:
        cursor.close()
        connection.close()


def append_history(result: dict, user_id: int | None = None) -> int:
    ensure_schema()
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO app_analysis_records (
                created_at,
                user_id,
                class_key,
                label,
                decision_text,
                upload_name,
                thumbnail_src,
                payload_encoding,
                result_payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                datetime.now(),
                user_id,
                result.get("class_key"),
                result["classification"]["label"],
                result["classification"]["decision_text"],
                result["upload_name"],
                result["segmentation"]["images"][0]["src"],
                "gzip-json",
                _encode_payload(result),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        cursor.close()
        connection.close()


def delete_history_record(record_id: int, user_id: int | None = None, allow_any: bool = False) -> None:
    ensure_schema()
    if not allow_any and not user_id:
        raise ValueError("当前账号没有删除这条记录的权限。")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        if allow_any:
            cursor.execute("SELECT id FROM app_analysis_records WHERE id = %s LIMIT 1", (record_id,))
        else:
            cursor.execute(
                "SELECT id FROM app_analysis_records WHERE id = %s AND user_id = %s LIMIT 1",
                (record_id, user_id),
            )
        if not cursor.fetchone():
            raise ValueError("这条识别记录不存在，或当前账号没有删除权限。")

        cursor.execute("DELETE FROM app_analysis_records WHERE id = %s", (record_id,))
        cursor.execute(
            "DELETE FROM app_latest_result WHERE payload = %s",
            (json.dumps({"record_id": record_id}, ensure_ascii=False),),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def save_latest_result(result: dict, user_id: int | None = None, record_id: int | None = None) -> None:
    ensure_schema()
    if record_id is None:
        payload = json.dumps(result, ensure_ascii=False)
    else:
        payload = json.dumps({"record_id": record_id}, ensure_ascii=False)
    cache_key = _cache_key_for_user(user_id)
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO app_latest_result (cache_key, user_id, payload)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE user_id = VALUES(user_id), payload = VALUES(payload)
            """,
            (cache_key, user_id, payload),
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def load_latest_result(user_id: int | None = None) -> dict | None:
    ensure_schema()
    cache_key = _cache_key_for_user(user_id)
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT payload
            FROM app_latest_result
            WHERE cache_key = %s
            LIMIT 1
            """,
            (cache_key,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        payload = json.loads(row[0])
        record_id = payload.get("record_id") if isinstance(payload, dict) else None
        if record_id:
            return load_analysis_record(record_id, user_id=user_id)
        return payload
    finally:
        cursor.close()
        connection.close()
