from __future__ import annotations

from webapp.classifier_service import get_classifier_service


def backend_ready() -> bool:
    try:
        get_classifier_service()
        return True
    except Exception:
        return False


def start_backend() -> None:
    # 分类链路已经切换为 Flask 进程内的 Python 推理模块，这里保留空实现以兼容旧调用。
    return None


def ensure_backend_ready(timeout_seconds: int = 40) -> None:
    _ = timeout_seconds
    get_classifier_service()


def classify_image(image_bytes: bytes, filename: str) -> dict:
    ensure_backend_ready()
    return get_classifier_service().classify_image(image_bytes, filename)
