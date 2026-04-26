from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, send_file, session, url_for

from webapp.assistant_service import ask_insect_assistant, assistant_status, get_ai_config_view, save_ai_config
from webapp.auth_store import (
    authenticate_user,
    count_users,
    create_user,
    delete_user_account,
    get_user_by_id,
    list_users,
    update_user_avatar,
)
from webapp.backend_client import classify_image, ensure_backend_ready
from webapp.content import CLASS_CATALOG, get_class_meta, resolve_class_key
from webapp.db import ensure_schema, load_db_config
from webapp.history_store import (
    append_history,
    count_history_records,
    delete_history_record,
    load_analysis_record,
    load_history,
    load_latest_result,
    save_latest_result,
)
from webapp.product_content import (
    ARTICLE_LIBRARY,
    ASSISTANT_QUICK_QUESTIONS,
    DISCOVER_TOOLS,
    DISTRIBUTION_SPECIES,
    FEED_TABS,
    GUIDE_CARDS,
    IDENTIFY_HIGHLIGHTS,
    MINE_ACTIONS,
    NEARBY_SITES,
    REFERENCE_LINKS,
    SEED_POSTS,
)
from webapp.segmentation_service import get_segmentation_service
from webapp.social_store import (
    count_follow_relations,
    count_posts,
    create_post,
    delete_post,
    follow_user,
    list_feed_posts,
    list_following,
    list_user_posts,
    search_friend_candidates,
)


PROJECT_ROOT = Path(__file__).resolve().parent
EXAMPLE_ROOT = PROJECT_ROOT / "_internal" / "demo" / "assets" / "examples"
HOME_BACKGROUND = PROJECT_ROOT / "fafu.jpg"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
app.secret_key = os.environ.get("APP_SECRET_KEY", "camouflage-insect-platform-2026")


def current_user() -> dict | None:
    return get_user_by_id(session.get("user_id"))


def current_user_id() -> int | None:
    user = current_user()
    return user["id"] if user else None


def is_admin(user: dict | None) -> bool:
    return bool(user and user.get("role") == "admin")


def is_mobile_client() -> bool:
    user_agent = (request.headers.get("User-Agent") or "").lower()
    mobile_markers = ["iphone", "android", "ipad", "mobile", "harmony", "miui"]
    return any(marker in user_agent for marker in mobile_markers)


def sample_cards() -> list[dict]:
    cards = []
    for item in CLASS_CATALOG:
        image_exists = (EXAMPLE_ROOT / item["sample_dir"] / "000_showcase.jpg").exists()
        cards.append(
            {
                "key": item["key"],
                "title": item["name_cn"],
                "subtitle": item["name_en"],
                "image_exists": image_exists,
                "image_url": url_for("sample_image", key=item["key"]) if image_exists else url_for("home_background"),
            }
        )
    return cards


def catalog_cards() -> list[dict]:
    cards = []
    for item in CLASS_CATALOG:
        image_exists = (EXAMPLE_ROOT / item["sample_dir"] / "000_showcase.jpg").exists()
        cards.append(
            {
                "key": item["key"],
                "title": item["name_cn"],
                "subtitle": item["name_en"],
                "clue": item["science"]["clue"],
                "observation": item["science"]["observation"],
                "role": item["science"]["role"],
                "impact": item["science"]["impact"],
                "advice": item["science"]["advice"],
                "image_exists": image_exists,
                "image_url": url_for("sample_image", key=item["key"]) if image_exists else url_for("home_background"),
            }
        )
    return cards


def nearby_sites() -> list[dict]:
    samples = {item["key"]: item for item in sample_cards()}
    sites = []
    for item in NEARBY_SITES:
        sample = samples.get(item["sample_key"])
        sites.append(
            {
                "title": item["title"],
                "subtitle": item["subtitle"],
                "x": item["x"],
                "y": item["y"],
                "sample_key": item["sample_key"],
                "image_url": sample["image_url"] if sample else url_for("home_background"),
            }
        )
    return sites


def build_distribution_species() -> list[dict]:
    sample_map = {item["key"]: item for item in sample_cards()}
    distribution = []
    for item in DISTRIBUTION_SPECIES:
        class_meta = get_class_meta(item["key"])
        sample = sample_map.get(item["key"])
        distribution.append(
            {
                "key": item["key"],
                "name_cn": item["name_cn"],
                "name_en": item["name_en"],
                "summary": item["summary"],
                "major_regions": item["major_regions"],
                "points": item["points"],
                "image_url": sample["image_url"] if sample else url_for("home_background"),
                "science": {
                    "title": class_meta["science"]["title"],
                    "clue": class_meta["science"]["clue"],
                    "observation": class_meta["science"]["observation"],
                    "role": class_meta["science"]["role"],
                    "impact": class_meta["science"]["impact"],
                    "advice": class_meta["science"]["advice"],
                },
            }
        )
    return distribution


def seed_feed_posts() -> list[dict]:
    sample_map = {item["key"]: item for item in sample_cards()}
    seeded = []
    for index, item in enumerate(SEED_POSTS, start=1):
        sample = sample_map.get(item["sample_key"])
        seeded.append(
            {
                "id": -index,
                "content": item["content"],
                "image_src": sample["image_url"] if sample else None,
                "tag_label": item["tag_label"],
                "created_at": item["created_at"],
                "author": {
                    "id": 0,
                    "username": item.get("username", f"seed-user-{index}"),
                    "display_name": item["author"],
                    "role": "user",
                },
                "is_self": False,
            }
        )
    if len(seeded) < 12:
        extra_specs = [
            ("校木带监测点", "早间补记", "bee", "58 分钟前", "主干道旁补拍到一张蜜蜂近景，今天的光线很稳，胸部绒毛和腹部体节比背景颜色更稳定。"),
            ("山地样方组", "林缘扫记", "phyllium", "1 小时前", "下午在山路转角处看到叶竹节虫，停驻在叶缘上的时候几乎和叶片走向完全一致，单看颜色很容易漏掉。"),
            ("农田样线组", "农田采样", "grasshopper", "1 小时前", "今天农田边缘的草地样线里，蝗虫和纺织娘同时出现，触角长度和身体比例比单纯看颜色更先要。"),
            ("水边观察员", "湿地追记", "dragonfly", "1 小时前", "水体边缘的蜻蜓活动还很高，今天补录到一张暖色背景下的样例，光照稳定时热力图会更明显。"),
            ("树干监测员", "树干样带", "cicada", "2 小时前", "树干上的蝉壳和成虫一起出现时，场景信息其实很重要，拍摄时保留周边纹理会更方便后续复核。"),
            ("花田记录员", "花田更新", "butterfly", "2 小时前", "花田边缘今天蝶类还是很活跃，新增的几张封面图既能用来展示，也能让首页动态区看起来更饱满。"),
        ]
        for offset, (author, tag_label, sample_key, created_at, content) in enumerate(extra_specs, start=len(seeded) + 1):
            sample = sample_map.get(sample_key)
            seeded.append(
                {
                    "id": -offset,
                    "content": content,
                    "image_src": sample["image_url"] if sample else None,
                    "tag_label": tag_label,
                    "created_at": created_at,
                    "author": {
                        "id": 0,
                        "username": f"seed-user-extra-{offset}",
                        "display_name": author,
                        "role": "user",
                    },
                    "is_self": False,
                }
            )
    return seeded


def build_admin_overview() -> dict:
    ensure_schema()
    return {
        "user_count": count_users(),
        "history_count": count_history_records(),
        "post_count": count_posts(),
        "follow_count": count_follow_relations(),
        "db_name": load_db_config()["database"],
        "db_host": load_db_config()["host"],
        "users": list_users(limit=20),
        "assistant": assistant_status(),
        "ai_config": get_ai_config_view(),
    }


def normalize_result_payload(result: dict | None) -> dict | None:
    if not result:
        return None

    normalized = dict(result)
    classification = dict(normalized.get("classification", {}))
    class_key = normalized.get("class_key") or resolve_class_key(classification.get("label", ""))
    class_meta = get_class_meta(class_key)
    merged_science = dict(class_meta.get("science", {}))
    legacy_generic_science = {
        "camouflage": {
            "当前结果暂未命中预设文案，建议结合分割图、热力图和局部证据综合判断。",
        },
        "clue": {
            "优先观察稳定的结构特征，再看颜色和背景关系。",
        },
        "observation": {
            "当前类别暂无补充观察信息，可结合拍摄场景与宿主环境继续研判。",
        },
        "role": {
            "暂缺生态角色信息。",
        },
        "impact": {
            "当前类别暂无风险说明，建议结合具体场景与寄主植物继续确认。",
        },
        "advice": {
            "现场处理以观察、记录和避免误判为主。",
        },
    }
    for field, value in (normalized.get("science") or {}).items():
        if value in legacy_generic_science.get(field, set()):
            continue
        merged_science[field] = value
    normalized["class_key"] = class_key
    normalized["classification"] = classification
    normalized["science"] = merged_science
    return normalized


def build_feed_posts(user_id: int | None, limit: int = 12) -> list[dict]:
    posts = list_feed_posts(viewer_user_id=user_id, limit=limit)
    seeded_posts = seed_feed_posts()
    if len(posts) >= limit:
        return posts
    return posts + seeded_posts[: max(0, limit - len(posts))]


def build_page_context(
    result: dict | None,
    error: str | None,
    initial_screen: str | None = None,
    record_id: int | None = None,
) -> dict:
    user = current_user()
    user_id = user["id"] if user else None
    mobile_client = is_mobile_client()
    selected_result = normalize_result_payload(result)
    if selected_result is None and record_id:
        selected_result = normalize_result_payload(
            load_analysis_record(record_id, user_id=user_id, allow_any=is_admin(user))
        )
    history_limit = 3 if mobile_client else 5
    history_entries = load_history(limit=history_limit, user_id=user_id) if user else []

    should_load_result = bool(selected_result) or record_id is not None or initial_screen == "result"
    latest_result = selected_result
    if latest_result is None and should_load_result:
        latest_result = (
            normalize_result_payload(load_latest_result(user_id))
            if user
            else normalize_result_payload(load_latest_result())
        )

    current_record_id = (
        latest_result.get("record_id")
        if latest_result and latest_result.get("record_id")
        else (history_entries[0]["record_id"] if history_entries else None)
    )
    result_url = (
        url_for("home", screen="result", record_id=current_record_id)
        if current_record_id
        else url_for("home", screen="result")
    )

    if initial_screen is None:
        if latest_result and (selected_result is not None or result is not None):
            initial_screen = "result"
        elif error:
            initial_screen = "identify"
        else:
            initial_screen = "identify"

    samples = sample_cards()
    context = {
        "sample_cards": samples,
        "featured_samples": samples[:6],
        "catalog_cards": catalog_cards(),
        "feed_posts": build_feed_posts(user_id, limit=12),
        "history_entries": history_entries,
        "identify_highlights": IDENTIFY_HIGHLIGHTS,
        "article_library": ARTICLE_LIBRARY[:10],
        "distribution_species": [],
        "distribution_default": None,
        "following_users": list_following(user_id, limit=12) if user and user.get("role") == "user" else [],
        "user_posts": list_user_posts(user_id, limit=12) if user and user.get("role") == "user" else [],
        "result": latest_result,
        "current_record_id": current_record_id,
        "result_url": result_url,
        "has_result": bool(current_record_id),
        "error": error,
        "is_mobile": mobile_client,
        "initial_screen": initial_screen,
        "guide_cards": GUIDE_CARDS,
        "reference_links": REFERENCE_LINKS,
        "feed_tabs": FEED_TABS,
        "discover_tools": DISCOVER_TOOLS,
        "mine_actions": MINE_ACTIONS,
        "nearby_sites": nearby_sites(),
        "assistant_quick_questions": ASSISTANT_QUICK_QUESTIONS,
        "assistant_state": assistant_status(),
        "current_user": user,
        "admin_overview": build_admin_overview() if is_admin(user) else None,
    }
    return context


def render_page(
    result: dict | None = None,
    error: str | None = None,
    initial_screen: str | None = None,
    record_id: int | None = None,
):
    return render_template("index.html", **build_page_context(result, error, initial_screen, record_id))


def has_frontend_dist() -> bool:
    return (FRONTEND_DIST / "index.html").exists()


def serve_frontend_index():
    return send_file(FRONTEND_DIST / "index.html")


def build_api_payload(
    result: dict | None = None,
    error: str | None = None,
    initial_screen: str | None = None,
    record_id: int | None = None,
) -> dict:
    return build_page_context(result, error, initial_screen, record_id)


def build_analyze_redirect_payload(result: dict, record_id: int, redirect_url: str) -> dict:
    return {
        "ok": True,
        "record_id": record_id,
        "redirect_url": redirect_url,
        "label": result["classification"]["label"],
        "decision_text": result["classification"]["decision_text"],
    }


def wants_json_response() -> bool:
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.accept_mimetypes.best == "application/json"
    )


def request_data() -> dict:
    return request.get_json(silent=True) or request.form.to_dict()


def file_to_data_uri(file_storage) -> str | None:
    if file_storage is None or not file_storage.filename:
        return None
    payload = file_storage.read()
    if not payload:
        return None
    mime_type = file_storage.mimetype or mimetypes.guess_type(file_storage.filename)[0] or "image/jpeg"
    encoded = base64.b64encode(payload).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def run_pipeline(image_bytes: bytes, filename: str) -> dict:
    ensure_backend_ready()
    segmentation = get_segmentation_service().analyze(image_bytes)
    classification = classify_image(segmentation["classification_bytes"], segmentation["classification_filename"])
    segmentation.pop("classification_bytes", None)
    segmentation.pop("classification_filename", None)
    class_key = resolve_class_key(classification["label"])
    class_meta = get_class_meta(class_key)
    return normalize_result_payload(
        {
            "segmentation": segmentation,
            "classification": classification,
            "science": class_meta["science"],
            "class_key": class_key,
            "upload_name": filename,
        }
    )


@app.get("/")
def home():
    if has_frontend_dist():
        return serve_frontend_index()
    return render_page(
        initial_screen=request.args.get("screen"),
        record_id=request.args.get("record_id", type=int),
    )


@app.get("/assets/<path:filename>")
def frontend_asset(filename: str):
    asset_path = FRONTEND_DIST / "assets" / filename
    if asset_path.exists():
        return send_file(asset_path)
    return ("", 404)


@app.get("/<path:filename>")
def frontend_public_file(filename: str):
    file_path = FRONTEND_DIST / filename
    if file_path.exists() and file_path.is_file():
        return send_file(file_path)
    return ("", 404)


@app.get("/api/bootstrap")
def api_bootstrap():
    response = jsonify(
        build_api_payload(
            initial_screen=request.args.get("screen"),
            record_id=request.args.get("record_id", type=int),
        )
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.post("/analyze")
def analyze_upload():
    image = request.files.get("image") or request.files.get("image_camera")
    if image is None or not image.filename:
        error_message = "请选择一张图片后再开始分析。"
        if wants_json_response():
            return jsonify({"ok": False, "error": error_message}), 400
        return render_page(error=error_message, initial_screen="identify")

    try:
        result = run_pipeline(image.read(), image.filename)
        record_id = append_history(result, user_id=current_user_id())
        result["record_id"] = record_id
        save_latest_result(result, user_id=current_user_id(), record_id=record_id)
        redirect_url = url_for("home", screen="result", record_id=record_id)
        if wants_json_response():
            return jsonify(build_analyze_redirect_payload(result, record_id, redirect_url))
        return redirect(redirect_url)
    except Exception as exc:  # noqa: BLE001
        if wants_json_response():
            return jsonify({"ok": False, "error": str(exc)}), 500
        return render_page(error=str(exc), initial_screen="identify")


@app.get("/sample/<key>")
def analyze_sample(key: str):
    item = next((card for card in CLASS_CATALOG if card["key"] == key), None)
    if item is None:
        return redirect(url_for("home"))

    sample_path = EXAMPLE_ROOT / item["sample_dir"] / "000_showcase.jpg"
    if not sample_path.exists():
        return render_page(error="标准图库资源缺失，请检查资源目录。", initial_screen="identify")

    try:
        result = run_pipeline(sample_path.read_bytes(), sample_path.name)
        record_id = append_history(result, user_id=current_user_id())
        result["record_id"] = record_id
        save_latest_result(result, user_id=current_user_id(), record_id=record_id)
        redirect_url = url_for("home", screen="result", record_id=record_id)
        if wants_json_response():
            return jsonify(build_analyze_redirect_payload(result, record_id, redirect_url))
        return redirect(redirect_url)
    except Exception as exc:  # noqa: BLE001
        if wants_json_response():
            return jsonify({"ok": False, "error": str(exc)}), 500
        return render_page(error=str(exc), initial_screen="samples")


@app.get("/sample-image/<key>")
def sample_image(key: str):
    item = next((card for card in CLASS_CATALOG if card["key"] == key), None)
    if item is None:
        return redirect(url_for("home"))
    return send_file(EXAMPLE_ROOT / item["sample_dir"] / "000_showcase.jpg")


@app.get("/fafu.jpg")
def home_background():
    return send_file(HOME_BACKGROUND)


@app.post("/api/analyze")
def api_analyze_upload():
    return analyze_upload()


@app.get("/api/sample/<key>/analyze")
def api_analyze_sample(key: str):
    return analyze_sample(key)


@app.post("/api/auth/register")
def api_auth_register():
    data = request_data()
    try:
        created = create_user(
            username=data.get("username", ""),
            password=data.get("password", ""),
            display_name=data.get("display_name", ""),
            role="user",
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    session["user_id"] = created["id"]
    return jsonify({"ok": True, "redirect_url": url_for("home", screen="mine"), "user": created})


@app.post("/api/auth/login")
def api_auth_login():
    data = request_data()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    login_scope = (data.get("login_scope") or "").strip()
    if not username or not password:
        return jsonify({"ok": False, "error": "请输入用户名和密码。"}), 400

    user = authenticate_user(username, password)
    if not user:
        return jsonify({"ok": False, "error": "账号或密码不正确。"}), 401
    if login_scope == "user-only" and user["role"] != "user":
        return jsonify({"ok": False, "error": "当前入口仅支持普通用户登录。"}), 403

    session["user_id"] = user["id"]
    redirect_screen = "admin" if user["role"] == "admin" else "mine"
    return jsonify({"ok": True, "redirect_url": url_for("home", screen=redirect_screen), "user": user})


@app.post("/api/auth/logout")
def api_auth_logout():
    session.clear()
    return jsonify({"ok": True, "redirect_url": url_for("home", screen="mine")})


@app.get("/api/friends/search")
def api_friend_search():
    user = current_user()
    if not user:
        return jsonify({"ok": False, "error": "请先登录普通用户账号后再搜索好友。"}), 401

    keyword = request.args.get("q", "")
    results = search_friend_candidates(keyword, user["id"])
    return jsonify({"ok": True, "results": results})


@app.post("/api/friends/follow")
def api_friend_follow():
    user = current_user()
    if not user or user.get("role") != "user":
        return jsonify({"ok": False, "error": "请先登录普通用户账号后再关注。"}), 401

    data = request_data()
    target_user_id = data.get("target_user_id")
    try:
        target_user_id = int(target_user_id)
        follow_user(user["id"], target_user_id)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, "following": list_following(user["id"], limit=24)})


@app.post("/api/posts")
def api_create_post():
    user = current_user()
    if not user or user.get("role") != "user":
        return jsonify({"ok": False, "error": "请先登录普通用户账号后再发布动态。"}), 401

    data = request_data()
    try:
        create_post(
            user_id=user["id"],
            content=data.get("content", ""),
            image_src=file_to_data_uri(request.files.get("image")),
            tag_label=data.get("tag_label", ""),
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, "redirect_url": url_for("home", screen="feed")})


@app.post("/api/posts/<int:post_id>/delete")
def api_delete_post(post_id: int):
    user = current_user()
    if not user:
        return jsonify({"ok": False, "error": "请先登录后再管理动态。"}), 401

    try:
        delete_post(post_id, user_id=user["id"], allow_any=is_admin(user))
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, "redirect_url": url_for("home", screen="feed")})


@app.post("/api/history/<int:record_id>/delete")
def api_delete_history(record_id: int):
    user = current_user()
    if not user:
        return jsonify({"ok": False, "error": "请先登录后再管理识别记录。"}), 401

    try:
        delete_history_record(record_id, user_id=user["id"], allow_any=is_admin(user))
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, "redirect_url": url_for("home", screen="history")})


@app.post("/api/account/delete")
def api_delete_account():
    user = current_user()
    if not user:
        return jsonify({"ok": False, "error": "当前没有可删除的登录账号。"}), 401

    try:
        delete_user_account(user["id"])
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    session.clear()
    return jsonify({"ok": True, "redirect_url": url_for("home", screen="mine")})


@app.post("/api/account/avatar")
def api_update_avatar():
    user = current_user()
    if not user:
        return jsonify({"ok": False, "error": "请先登录普通用户账号后再上传头像。"}), 401

    avatar_src = file_to_data_uri(request.files.get("avatar"))
    if not avatar_src:
        return jsonify({"ok": False, "error": "请选择一张头像图片后再上传。"}), 400

    updated_user = update_user_avatar(user["id"], avatar_src)
    return jsonify({"ok": True, "current_user": updated_user, "redirect_url": url_for("home", screen="mine")})


@app.post("/api/admin/users")
def api_admin_create_user():
    user = current_user()
    if not is_admin(user):
        return jsonify({"ok": False, "error": "当前账号没有管理员权限。"}), 403

    data = request_data()
    try:
        created = create_user(
            username=data.get("username", ""),
            password=data.get("password", ""),
            display_name=data.get("display_name", ""),
            role=data.get("role", "user"),
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, "user": created, "users": list_users(limit=20)})


@app.post("/api/admin/users/<int:target_user_id>/delete")
def api_admin_delete_user(target_user_id: int):
    user = current_user()
    if not is_admin(user):
        return jsonify({"ok": False, "error": "当前账号没有管理员权限。"}), 403
    if target_user_id == user["id"]:
        return jsonify({"ok": False, "error": "请在账号中心处理当前登录账号。"}), 400

    try:
        delete_user_account(target_user_id)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, "users": list_users(limit=20)})


@app.post("/api/admin/ai-config")
def api_admin_ai_config():
    user = current_user()
    if not is_admin(user):
        return jsonify({"ok": False, "error": "当前账号没有管理员权限。"}), 403

    data = request_data()
    try:
        config_view = save_ai_config(
            provider=data.get("provider", ""),
            api_base=data.get("api_base", ""),
            model=data.get("model", ""),
            api_key=data.get("api_key", ""),
            temperature=data.get("temperature", 0.4),
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, "config": config_view})


@app.post("/api/assistant/ask")
def api_assistant_ask():
    data = request_data()
    question = (data.get("question") or "").strip()
    user = current_user()
    user_id = user["id"] if user else None
    record_id = data.get("record_id")
    try:
        record_id = int(record_id) if record_id not in (None, "", "null") else None
    except (TypeError, ValueError):
        record_id = None

    if record_id:
        result = normalize_result_payload(
            load_analysis_record(record_id, user_id=user_id, allow_any=is_admin(user))
        )
    else:
        result = (
            normalize_result_payload(load_latest_result(user_id))
            if user_id
            else normalize_result_payload(load_latest_result())
        )

    if not result:
        return jsonify({"ok": False, "error": "当前没有可用于问答的识别结果，请先完成一次识别。"}), 400

    try:
        answer_payload = ask_insect_assistant(question, result)
        return jsonify({"ok": True, **answer_payload})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)}), 500


if __name__ == "__main__":
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", "7863"))
    app.run(host=host, port=port, debug=False)
