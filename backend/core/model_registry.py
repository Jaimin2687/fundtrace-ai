from dataclasses import dataclass
import os

from .config import get_settings


@dataclass(frozen=True)
class ModelInfo:
    source: str
    path: str


def resolve_model_source(preferred: str) -> str:
    normalized = preferred.strip().lower()
    if normalized not in {"auto", "elliptic", "paysim"}:
        raise ValueError("MODEL_SOURCE must be one of: auto, elliptic, paysim")
    if normalized == "auto":
        return "paysim" if os.path.exists("data/paysim_model.json") else "elliptic"
    return normalized


def model_path_for_source(source: str) -> str:
    if source == "paysim":
        return "data/paysim_model.json"
    return "data/fraud_model.json"


def get_model_info() -> ModelInfo:
    settings = get_settings()
    source = resolve_model_source(settings.MODEL_SOURCE)
    return ModelInfo(source=source, path=model_path_for_source(source))


def model_exists(model_info: ModelInfo) -> bool:
    return os.path.exists(model_info.path)
