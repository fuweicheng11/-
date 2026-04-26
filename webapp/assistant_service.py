from __future__ import annotations

import json
import os
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AI_CONFIG_FILE = PROJECT_ROOT / "runtime" / "ai_config.json"

DEFAULT_AI_CONFIG = {
    "provider": "deepseek",
    "api_base": "https://api.deepseek.com/chat/completions",
    "model": "deepseek-chat",
    "api_key": "",
    "temperature": 0.4,
}


def load_ai_config() -> dict:
    config = dict(DEFAULT_AI_CONFIG)
    if AI_CONFIG_FILE.exists():
        try:
            config.update(json.loads(AI_CONFIG_FILE.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass

    env_map = {
        "provider": os.getenv("CAMOUFLAGE_AI_PROVIDER"),
        "api_base": os.getenv("CAMOUFLAGE_AI_BASE"),
        "model": os.getenv("CAMOUFLAGE_AI_MODEL"),
        "api_key": os.getenv("CAMOUFLAGE_AI_KEY") or os.getenv("DEEPSEEK_API_KEY"),
        "temperature": os.getenv("CAMOUFLAGE_AI_TEMPERATURE"),
    }

    for key, value in env_map.items():
        if value not in (None, ""):
            config[key] = float(value) if key == "temperature" else value

    return config


def ensure_ai_config_file() -> None:
    AI_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not AI_CONFIG_FILE.exists():
        AI_CONFIG_FILE.write_text(json.dumps(DEFAULT_AI_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")


def assistant_status() -> dict:
    ensure_ai_config_file()
    config = load_ai_config()
    return {
        "provider": config["provider"],
        "model": config["model"],
        "api_base": config["api_base"],
        "temperature": config["temperature"],
        "has_api_key": bool(config.get("api_key")),
        "enabled": bool(config.get("api_key")),
    }


def get_ai_config_view() -> dict:
    ensure_ai_config_file()
    config = load_ai_config()
    api_key = config.get("api_key", "")
    return {
        "provider": config["provider"],
        "api_base": config["api_base"],
        "model": config["model"],
        "temperature": config["temperature"],
        "api_key_masked": f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) >= 12 else ("已配置" if api_key else "未配置"),
        "enabled": bool(api_key),
    }


def save_ai_config(provider: str, api_base: str, model: str, api_key: str, temperature: float) -> dict:
    ensure_ai_config_file()
    provider = (provider or "deepseek").strip() or "deepseek"
    api_base = (api_base or DEFAULT_AI_CONFIG["api_base"]).strip()
    model = (model or DEFAULT_AI_CONFIG["model"]).strip()
    api_key = (api_key or "").strip()
    try:
        temperature = float(temperature)
    except (TypeError, ValueError):
        raise ValueError("温度参数需要是数字。")

    payload = {
        "provider": provider,
        "api_base": api_base,
        "model": model,
        "api_key": api_key,
        "temperature": max(0.0, min(temperature, 1.5)),
    }
    AI_CONFIG_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return get_ai_config_view()


def _science_context(result: dict) -> dict:
    science = result.get("science", {})
    classification = result.get("classification", {})
    return {
        "label": classification.get("label", "当前识别对象"),
        "decision": classification.get("decision_text", ""),
        "role": science.get("role", ""),
        "impact": science.get("impact", ""),
        "advice": science.get("advice", ""),
        "camouflage": science.get("camouflage", ""),
        "clue": science.get("clue", ""),
        "observation": science.get("observation", ""),
    }


def build_local_answer(question: str, result: dict) -> str:
    info = _science_context(result)
    label = info["label"]
    lower_question = question.strip().lower()

    if any(keyword in question for keyword in ["危害", "害虫", "益虫", "好虫", "坏虫"]) or "harm" in lower_question:
        return (
            f"{label}的生态角色判断是：{info['role']}\n\n"
            f"风险与影响：{info['impact']}\n\n"
            f"现场建议：{info['advice']}"
        )

    if any(keyword in question for keyword in ["怎么认", "识别", "区别", "混淆"]) or "identify" in lower_question:
        return (
            f"{label}的识别可以先看稳定结构，而不是先看颜色。\n\n"
            f"识别线索：{info['clue']}\n\n"
            f"伪装方式：{info['camouflage']}"
        )

    if any(keyword in question for keyword in ["哪里", "环境", "习性", "什么时候"]) or "habitat" in lower_question:
        return (
            f"{label}的自然观察信息如下：\n\n"
            f"{info['observation']}\n\n"
            f"如果用于现场判断，可以再结合拍摄位置、宿主植物和活动时间一起确认。"
        )

    return (
        f"当前识别对象为 {label}。\n\n"
        f"生态角色：{info['role']}\n\n"
        f"风险与影响：{info['impact']}\n\n"
        f"识别线索：{info['clue']}\n\n"
        f"现场建议：{info['advice']}"
    )


def _build_remote_messages(question: str, result: dict) -> list[dict]:
    info = _science_context(result)
    system_prompt = (
        "你是一名昆虫识别应用中的生态解读助手。"
        "回答要准确、自然、简洁，避免夸张和不确定结论。"
        "如果信息不足，要明确说明依据来自当前识别结果与内置知识，不要编造。"
    )
    context_prompt = (
        f"当前识别对象：{info['label']}\n"
        f"模型判断：{info['decision']}\n"
        f"生态角色：{info['role']}\n"
        f"风险与影响：{info['impact']}\n"
        f"现场建议：{info['advice']}\n"
        f"伪装方式：{info['camouflage']}\n"
        f"识别线索：{info['clue']}\n"
        f"自然观察：{info['observation']}"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": context_prompt},
        {"role": "user", "content": question.strip()},
    ]


def ask_insect_assistant(question: str, result: dict) -> dict:
    question = question.strip()
    if not question:
        raise ValueError("请输入想继续了解的问题。")

    ensure_ai_config_file()
    config = load_ai_config()
    if not config.get("api_key"):
        return {
            "answer": build_local_answer(question, result),
            "mode": "local",
            "provider": "local-knowledge",
            "model": "built-in",
        }

    response = requests.post(
        config["api_base"],
        headers={
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        },
        json={
            "model": config["model"],
            "messages": _build_remote_messages(question, result),
            "temperature": config["temperature"],
            "stream": False,
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    answer = payload["choices"][0]["message"]["content"].strip()
    return {
        "answer": answer,
        "mode": "remote",
        "provider": config["provider"],
        "model": config["model"],
    }
