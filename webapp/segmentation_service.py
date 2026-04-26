from __future__ import annotations

import base64
import sys
import warnings
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEGMENT_ROOT = PROJECT_ROOT / "segmentation" / "alg06_run"
MODEL_PATH = PROJECT_ROOT / "segmentation" / "models" / "MODEL06_RUN_best.pth"

if str(SEGMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(SEGMENT_ROOT))

warnings.filterwarnings("ignore", category=FutureWarning, module="timm")

from lib.Network import Network  # noqa: E402


def _to_data_uri(image_bgr: np.ndarray, ext: str = ".jpg", quality: int = 95) -> str:
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality] if ext.lower() in {".jpg", ".jpeg"} else []
    ok, encoded = cv2.imencode(ext, image_bgr, encode_params)
    if not ok:
        raise RuntimeError("图片编码失败。")
    mime = "image/png" if ext.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(encoded.tobytes()).decode('ascii')}"


def _largest_components(mask: np.ndarray, min_area_ratio: float = 0.001) -> np.ndarray:
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    if num_labels <= 1:
        return mask
    refined = np.zeros_like(mask, dtype=np.uint8)
    min_area = mask.shape[0] * mask.shape[1] * min_area_ratio
    for idx in range(1, num_labels):
        if stats[idx, cv2.CC_STAT_AREA] >= min_area:
            refined[labels == idx] = 1
    return refined if refined.any() else mask


class SegmentationService:
    def __init__(self) -> None:
        self.device = torch.device("cpu")
        self.model = Network(channels=192).to(self.device)
        state = torch.load(MODEL_PATH, map_location=self.device)
        self.model.load_state_dict(state, strict=False)
        self.model.eval()
        self.mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(3, 1, 1)
        self.std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(3, 1, 1)

    def _predict_mask(self, image_bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        orig_h, orig_w = image_bgr.shape[:2]
        resized = cv2.resize(image_bgr, (384, 384), interpolation=cv2.INTER_LINEAR)
        tensor = resized[:, :, ::-1].transpose((2, 0, 1)).astype(np.float32) / 255.0
        tensor = (tensor - self.mean) / self.std
        tensor = torch.from_numpy(tensor).unsqueeze(0).to(self.device)

        with torch.no_grad():
            pred_list = self.model(tensor)
            pred = F.interpolate(pred_list[4], size=(orig_h, orig_w), mode="bilinear", align_corners=False)
            pred = pred.sigmoid().cpu().numpy().squeeze().astype(np.float32)

        pred = (pred - pred.min()) / (pred.max() - pred.min() + 1e-8)
        mask = (pred >= 0.5).astype(np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        mask = _largest_components(mask)
        return pred, mask

    @staticmethod
    def _mask_bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
        ys, xs = np.where(mask > 0)
        if len(xs) == 0:
            return 0, 0, mask.shape[1], mask.shape[0]
        return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1

    @staticmethod
    def _expand_bbox(x1: int, y1: int, x2: int, y2: int, width: int, height: int) -> tuple[int, int, int, int]:
        pad_x = max(24, int((x2 - x1) * 0.18))
        pad_y = max(24, int((y2 - y1) * 0.18))
        return (
            max(0, x1 - pad_x),
            max(0, y1 - pad_y),
            min(width, x2 + pad_x),
            min(height, y2 + pad_y),
        )

    def analyze(self, image_bytes: bytes) -> dict:
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image_bgr = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image_bgr is None:
            raise RuntimeError("上传图片无法读取，请换一张再试。")

        probability, mask = self._predict_mask(image_bgr)
        x1, y1, x2, y2 = self._mask_bbox(mask)
        x1, y1, x2, y2 = self._expand_bbox(x1, y1, x2, y2, image_bgr.shape[1], image_bgr.shape[0])
        crop_bgr = image_bgr[y1:y2, x1:x2].copy()

        sky = np.full_like(image_bgr, (236, 245, 249), dtype=np.uint8)
        softened = cv2.addWeighted(image_bgr, 0.18, sky, 0.82, 0.0)
        cutout_bgr = image_bgr.copy()
        cutout_bgr[mask == 0] = softened[mask == 0]

        overlay = image_bgr.copy()
        tint = np.zeros_like(image_bgr)
        tint[:, :] = (210, 237, 246)
        overlay = np.where(mask[:, :, None] == 1, cv2.addWeighted(overlay, 0.55, tint, 0.45, 0.0), overlay)
        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay, contours, -1, (97, 171, 203), 2)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (82, 151, 184), 2)

        mask_preview = (probability * 255.0).astype(np.uint8)
        mask_preview = cv2.applyColorMap(mask_preview, cv2.COLORMAP_OCEAN)

        ok, crop_encoded = cv2.imencode(".jpg", crop_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        if not ok:
            raise RuntimeError("分类裁切图生成失败。")

        area_ratio = float(mask.sum()) / float(mask.shape[0] * mask.shape[1])
        return {
            "classification_bytes": crop_encoded.tobytes(),
            "classification_filename": "segmented_focus.jpg",
            "stats": {
                "mask_ratio": f"{area_ratio * 100:.1f}%",
                "crop_size": f"{crop_bgr.shape[1]} × {crop_bgr.shape[0]}",
                "focus_box": f"{x2 - x1} × {y2 - y1}",
            },
            "images": [
                {"label": "原图", "src": _to_data_uri(image_bgr)},
                {"label": "分割叠加", "src": _to_data_uri(overlay)},
                {"label": "主体抠出", "src": _to_data_uri(cutout_bgr)},
                {"label": "分类裁切", "src": _to_data_uri(crop_bgr)},
            ],
            "mask_heatmap": _to_data_uri(mask_preview),
        }


_SERVICE: SegmentationService | None = None


def get_segmentation_service() -> SegmentationService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = SegmentationService()
    return _SERVICE
