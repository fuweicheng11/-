from __future__ import annotations

import base64
import json
import sys
import warnings
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn

from webapp.content import CLASS_CATALOG, resolve_class_key


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONVNEXT_ROOT = PROJECT_ROOT / "_internal" / "master" / "ConvNeXt-main"
DINOV2_ROOT = PROJECT_ROOT / "_internal" / "master" / "dinov2-main"
FUSION_CKPT = PROJECT_ROOT / "runtime" / "CamouflageDriveQ" / "08" / "fusion_results" / "fusion_best.pth"
REJECTION_RULE = PROJECT_ROOT / "runtime" / "CamouflageDriveQ" / "08" / "evaluation_results" / "fusion" / "rejection_summary.json"

if str(CONVNEXT_ROOT) not in sys.path:
    sys.path.insert(0, str(CONVNEXT_ROOT))
if str(DINOV2_ROOT) not in sys.path:
    sys.path.insert(0, str(DINOV2_ROOT))

warnings.filterwarnings("ignore", category=FutureWarning, module="timm")
warnings.filterwarnings("ignore", message=".*Overwriting convnext_.*")
warnings.filterwarnings("ignore", message=".*xFormers is not available.*")

from models.convnext import convnext_base  # noqa: E402
from dinov2.hub.backbones import dinov2_vitb14_reg  # noqa: E402


IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
CONVNEXT_INPUT = 224
DINO_INPUT = 518
DEFAULT_MARGIN_THRESHOLD = 0.306215

ATTRIBUTE_LABELS = {
    "leaf_like": "叶片拟态",
    "stick_like": "枝条拟态",
    "elongated_body": "细长体型",
    "wing_pattern_visible": "翅纹明显",
    "edge_background_consistent": "边缘贴背景",
    "leaf_margin_mimic": "叶缘拟态",
}

DISPLAY_BY_KEY = {
    item["key"]: f'{item["name_cn"]} ({item["name_en"]})'
    for item in CLASS_CATALOG
}


def _to_data_uri(image_bgr: np.ndarray, ext: str = ".jpg", quality: int = 92) -> str:
    params = [int(cv2.IMWRITE_JPEG_QUALITY), quality] if ext.lower() in {".jpg", ".jpeg"} else []
    ok, encoded = cv2.imencode(ext, image_bgr, params)
    if not ok:
        raise RuntimeError("分类证据图编码失败。")
    mime = "image/png" if ext.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(encoded.tobytes()).decode('ascii')}"


def _normalize_map(values: np.ndarray) -> np.ndarray:
    values = values.astype(np.float32)
    values -= values.min()
    denom = values.max() + 1e-8
    if denom <= 0:
        return np.zeros_like(values, dtype=np.float32)
    return values / denom


def _overlay_heatmap(image_bgr: np.ndarray, heatmap: np.ndarray, alpha: float = 0.42) -> np.ndarray:
    heat_uint8 = np.clip(heatmap * 255.0, 0, 255).astype(np.uint8)
    colored = cv2.applyColorMap(heat_uint8, cv2.COLORMAP_JET)
    return cv2.addWeighted(image_bgr, 1.0 - alpha, colored, alpha, 0.0)


def _resize_rgb(image_rgb: np.ndarray, size: int) -> np.ndarray:
    return cv2.resize(image_rgb, (size, size), interpolation=cv2.INTER_LINEAR)


def _to_tensor(image_rgb: np.ndarray) -> torch.Tensor:
    array = image_rgb.astype(np.float32) / 255.0
    array = (array - IMAGENET_MEAN) / IMAGENET_STD
    array = array.transpose((2, 0, 1))
    return torch.from_numpy(array).float().unsqueeze(0)


def _decode_bgr(image_bytes: bytes) -> np.ndarray:
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image_bgr = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise RuntimeError("分类输入图像无法读取，请更换图片后重试。")
    return image_bgr


def _entropy(probs: np.ndarray) -> float:
    safe = np.clip(probs, 1e-8, 1.0)
    return float(-(safe * np.log(safe)).sum() / np.log(len(probs)))


def _load_margin_threshold() -> float:
    if not REJECTION_RULE.exists():
        return DEFAULT_MARGIN_THRESHOLD
    try:
        payload = json.loads(REJECTION_RULE.read_text(encoding="utf-8"))
        return float(payload.get("threshold", DEFAULT_MARGIN_THRESHOLD))
    except Exception:
        return DEFAULT_MARGIN_THRESHOLD


def _format_display_label(raw_label: str) -> str:
    key = resolve_class_key(raw_label)
    return DISPLAY_BY_KEY.get(key, raw_label)


class ConvNeXtBranch(nn.Module):
    def __init__(self, num_classes: int) -> None:
        super().__init__()
        self.model = convnext_base(pretrained=False, num_classes=num_classes)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        current = x
        for idx in range(4):
            current = self.model.downsample_layers[idx](current)
            current = self.model.stages[idx](current)
        feature_map = current
        global_feature = self.model.norm(feature_map.mean([-2, -1]))
        logits = self.model.head(global_feature)
        return logits, global_feature, feature_map


class DINOv2Branch(nn.Module):
    def __init__(self, num_classes: int) -> None:
        super().__init__()
        self.model = dinov2_vitb14_reg(pretrained=False)
        self.model.head = nn.Linear(self.model.embed_dim, num_classes)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        features = self.model.forward_features(x)
        cls_feature = features["x_norm_clstoken"]
        patch_tokens = features["x_norm_patchtokens"]
        logits = self.model.head(cls_feature)
        return logits, cls_feature, patch_tokens


class GatingFusionTrunk(nn.Module):
    def __init__(self, num_classes: int, feature_proj_dim: int, logit_proj_dim: int, hidden_dim: int, dropout: float) -> None:
        super().__init__()
        branch_dim = feature_proj_dim + logit_proj_dim
        concat_dim = branch_dim * 2
        self.global_feature_proj = nn.Sequential(nn.LayerNorm(1024), nn.Linear(1024, feature_proj_dim))
        self.local_feature_proj = nn.Sequential(nn.LayerNorm(768), nn.Linear(768, feature_proj_dim))
        self.global_logit_proj = nn.Sequential(nn.LayerNorm(num_classes), nn.Linear(num_classes, logit_proj_dim))
        self.local_logit_proj = nn.Sequential(nn.LayerNorm(num_classes), nn.Linear(num_classes, logit_proj_dim))
        self.gate = nn.Sequential(
            nn.LayerNorm(concat_dim),
            nn.Linear(concat_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, branch_dim),
        )
        self.classifier = nn.Sequential(
            nn.LayerNorm(branch_dim),
            nn.Linear(branch_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(
        self,
        global_feature: torch.Tensor,
        global_logits: torch.Tensor,
        local_feature: torch.Tensor,
        local_logits: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        global_repr = torch.cat(
            [self.global_feature_proj(global_feature), self.global_logit_proj(global_logits)],
            dim=1,
        )
        local_repr = torch.cat(
            [self.local_feature_proj(local_feature), self.local_logit_proj(local_logits)],
            dim=1,
        )
        gate_logits = self.gate(torch.cat([global_repr, local_repr], dim=1))
        gate_weights = torch.sigmoid(gate_logits)
        fused_feature = gate_weights * global_repr + (1.0 - gate_weights) * local_repr
        fused_logits = self.classifier(fused_feature)
        return fused_logits, fused_feature, gate_weights, global_repr, local_repr


class MultiTaskHead(nn.Module):
    def __init__(self, fused_dim: int, hidden_dim: int, attr_dim: int, dropout: float) -> None:
        super().__init__()
        self.binary_head = nn.Sequential(
            nn.LayerNorm(fused_dim),
            nn.Linear(fused_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, attr_dim),
        )

    def forward(self, fused_feature: torch.Tensor) -> torch.Tensor:
        return self.binary_head(fused_feature)


class FusionClassifier(nn.Module):
    def __init__(
        self,
        num_classes: int,
        feature_proj_dim: int,
        logit_proj_dim: int,
        hidden_dim: int,
        attr_hidden_dim: int,
        dropout: float,
        attr_dim: int,
    ) -> None:
        super().__init__()
        self.convnext = ConvNeXtBranch(num_classes)
        self.dinov2 = DINOv2Branch(num_classes)
        self.fusion_trunk = GatingFusionTrunk(
            num_classes=num_classes,
            feature_proj_dim=feature_proj_dim,
            logit_proj_dim=logit_proj_dim,
            hidden_dim=hidden_dim,
            dropout=dropout,
        )
        fused_dim = feature_proj_dim + logit_proj_dim
        self.multitask_head = MultiTaskHead(
            fused_dim=fused_dim,
            hidden_dim=attr_hidden_dim,
            attr_dim=attr_dim,
            dropout=dropout,
        )

    def forward(self, global_image: torch.Tensor, local_image: torch.Tensor) -> dict[str, torch.Tensor]:
        global_logits, global_feature, feature_map = self.convnext(global_image)
        local_logits, local_feature, patch_tokens = self.dinov2(local_image)
        fused_logits, fused_feature, gate_weights, global_repr, local_repr = self.fusion_trunk(
            global_feature,
            global_logits,
            local_feature,
            local_logits,
        )
        binary_logits = self.multitask_head(fused_feature)
        return {
            "global_logits": global_logits,
            "global_feature": global_feature,
            "feature_map": feature_map,
            "local_logits": local_logits,
            "local_feature": local_feature,
            "patch_tokens": patch_tokens,
            "fused_logits": fused_logits,
            "fused_feature": fused_feature,
            "gate_weights": gate_weights,
            "global_repr": global_repr,
            "local_repr": local_repr,
            "binary_logits": binary_logits,
        }


class ClassifierService:
    def __init__(self) -> None:
        if not FUSION_CKPT.exists():
            raise RuntimeError(f"分类权重缺失：{FUSION_CKPT}")

        checkpoint = torch.load(FUSION_CKPT, map_location="cpu")
        self.classes = list(checkpoint.get("classes") or [])
        self.args = checkpoint.get("args") or {}
        self.binary_attributes = [item.strip() for item in str(self.args.get("binary_attributes", "")).split(",") if item.strip()]
        self.margin_threshold = _load_margin_threshold()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = FusionClassifier(
            num_classes=len(self.classes),
            feature_proj_dim=int(self.args.get("feature_proj_dim", 256)),
            logit_proj_dim=int(self.args.get("logit_proj_dim", 64)),
            hidden_dim=int(self.args.get("hidden_dim", 512)),
            attr_hidden_dim=int(self.args.get("attr_hidden_dim", 256)),
            dropout=float(self.args.get("dropout", 0.2)),
            attr_dim=len(self.binary_attributes),
        ).to(self.device)

        load_status = self.model.load_state_dict(checkpoint["model_state_dict"], strict=False)
        if load_status.unexpected_keys:
            raise RuntimeError(f"分类模型加载失败，存在未处理参数：{load_status.unexpected_keys[:5]}")
        self.model.eval()

    def _attribute_labels(self, attr_probs: np.ndarray) -> list[str]:
        labels = []
        for key, score in zip(self.binary_attributes, attr_probs.tolist()):
            if score >= 0.5:
                labels.append(ATTRIBUTE_LABELS.get(key, key))
        return labels

    def _convnext_heatmap(self, feature_map: torch.Tensor, class_index: int, output_size: tuple[int, int]) -> np.ndarray:
        weight = self.model.convnext.model.head.weight[class_index].detach().cpu().numpy()
        fmap = feature_map[0].detach().cpu().numpy()
        cam = np.tensordot(weight, fmap, axes=(0, 0))
        cam = np.maximum(cam, 0.0)
        cam = _normalize_map(cam)
        return cv2.resize(cam, output_size, interpolation=cv2.INTER_LINEAR)

    def _dinov2_heatmap(self, patch_tokens: torch.Tensor, class_index: int, output_size: tuple[int, int]) -> np.ndarray:
        head_weight = self.model.dinov2.model.head.weight[class_index].detach().cpu().numpy()
        head_bias = float(self.model.dinov2.model.head.bias[class_index].detach().cpu())
        patches = patch_tokens[0].detach().cpu().numpy()
        scores = patches @ head_weight + head_bias
        side = int(np.sqrt(scores.shape[0]))
        heatmap = scores.reshape(side, side)
        heatmap = _normalize_map(heatmap)
        return cv2.resize(heatmap, output_size, interpolation=cv2.INTER_CUBIC)

    @staticmethod
    def _local_focus_box(local_map: np.ndarray) -> tuple[int, int, int, int] | None:
        mask = (local_map >= max(0.72, float(local_map.mean() + local_map.std() * 0.5))).astype(np.uint8)
        ys, xs = np.where(mask > 0)
        if len(xs) > 0 and len(ys) > 0:
            return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
        return None

    @staticmethod
    def _build_local_box(image_bgr: np.ndarray, local_map: np.ndarray) -> np.ndarray:
        boxed = image_bgr.copy()
        box = ClassifierService._local_focus_box(local_map)
        if box:
            x1, y1, x2, y2 = box
            cv2.rectangle(boxed, (x1, y1), (x2, y2), (64, 214, 255), 3)
        return boxed

    @staticmethod
    def _build_local_heatmap(image_bgr: np.ndarray, local_map: np.ndarray) -> np.ndarray:
        return _overlay_heatmap(image_bgr, local_map, alpha=0.48)

    def classify_image(self, image_bytes: bytes, filename: str) -> dict:
        image_bgr = _decode_bgr(image_bytes)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        orig_h, orig_w = image_bgr.shape[:2]

        global_tensor = _to_tensor(_resize_rgb(image_rgb, CONVNEXT_INPUT)).to(self.device)
        local_tensor = _to_tensor(_resize_rgb(image_rgb, DINO_INPUT)).to(self.device)

        with torch.inference_mode():
            outputs = self.model(global_tensor, local_tensor)

        probs = torch.softmax(outputs["fused_logits"], dim=1)[0].detach().cpu().numpy()
        top_indices = probs.argsort()[::-1]
        top1_index = int(top_indices[0])
        top2_index = int(top_indices[1]) if len(top_indices) > 1 else top1_index
        top1_prob = float(probs[top1_index])
        margin = float(top1_prob - probs[top2_index])
        entropy = _entropy(probs)
        accepted = margin >= self.margin_threshold

        top1_raw = self.classes[top1_index]
        top1_display = _format_display_label(top1_raw)
        result_label = top1_display if accepted else "拒识 / 结果不确定"
        decision_text = "识别通过" if accepted else "拒识"

        global_branch_probs = torch.softmax(outputs["global_logits"], dim=1)[0].detach().cpu().numpy()
        local_branch_probs = torch.softmax(outputs["local_logits"], dim=1)[0].detach().cpu().numpy()
        global_branch_label = _format_display_label(self.classes[int(global_branch_probs.argmax())])
        local_branch_label = _format_display_label(self.classes[int(local_branch_probs.argmax())])

        attr_probs = torch.sigmoid(outputs["binary_logits"])[0].detach().cpu().numpy()
        attr_labels = self._attribute_labels(attr_probs)

        global_map = self._convnext_heatmap(outputs["feature_map"], top1_index, (orig_w, orig_h))
        local_map = self._dinov2_heatmap(outputs["patch_tokens"], top1_index, (orig_w, orig_h))

        evidence_images = [
            {"label": "全局热力图", "src": _to_data_uri(_overlay_heatmap(image_bgr, global_map))},
            {"label": "主体裁切图", "src": _to_data_uri(image_bgr)},
            {"label": "定位框结果", "src": _to_data_uri(self._build_local_box(image_bgr, local_map))},
            {"label": "局部热力图", "src": _to_data_uri(self._build_local_heatmap(image_bgr, local_map))},
        ]

        top3 = []
        for idx in top_indices[:3]:
            score = float(probs[int(idx)])
            top3.append(
                {
                    "name": _format_display_label(self.classes[int(idx)]),
                    "score": f"{score * 100:.1f}%",
                    "width": f"{score * 100:.1f}%",
                }
            )

        rule_parts = [
            f"ConvNeXt 分支偏向 {global_branch_label}",
            f"DINOv2 分支偏向 {local_branch_label}",
            f"融合边际差为 {margin:.3f}（阈值 {self.margin_threshold:.3f}）",
        ]
        if attr_labels:
            rule_parts.append(f"属性线索：{'、'.join(attr_labels)}")

        return {
            "label": result_label,
            "decision_text": decision_text,
            "accepted": accepted,
            "meta": {
                "source_name": filename,
                "original_size": f"{orig_w} x {orig_h}",
                "inference_size": f"ConvNeXt {CONVNEXT_INPUT} x {CONVNEXT_INPUT} / DINOv2 {DINO_INPUT} x {DINO_INPUT}",
            },
            "metrics": [
                {"label": "Top-1 预测", "value": top1_display},
                {"label": "置信度", "value": f"{top1_prob:.3f}"},
                {"label": "边际差", "value": f"{margin:.3f}"},
                {"label": "熵值", "value": f"{entropy:.3f}"},
            ],
            "rule_text": "；".join(rule_parts),
            "top3": top3,
            "evidence_images": evidence_images,
            "top_candidate": top1_display,
            "branches": {
                "convnext": global_branch_label,
                "dinov2": local_branch_label,
            },
            "attributes": [
                {
                    "key": key,
                    "label": ATTRIBUTE_LABELS.get(key, key),
                    "score": round(float(score), 4),
                }
                for key, score in zip(self.binary_attributes, attr_probs.tolist())
            ],
        }


_SERVICE: ClassifierService | None = None


def get_classifier_service() -> ClassifierService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = ClassifierService()
    return _SERVICE
