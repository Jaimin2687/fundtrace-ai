from pathlib import Path
from typing import Iterable, Optional


DATA_DIR = Path(__file__).resolve().parent
ELLIPTIC_DIR = DATA_DIR / "elliptic_bitcoin_dataset"


def resolve_dataset_path(filename: str, search_dirs: Optional[Iterable[Path]] = None) -> Optional[Path]:
    dirs = list(search_dirs) if search_dirs is not None else [DATA_DIR, ELLIPTIC_DIR]
    for directory in dirs:
        candidate = directory / filename
        if candidate.exists():
            return candidate
    return None


def require_dataset_path(filename: str, search_dirs: Optional[Iterable[Path]] = None) -> Path:
    path = resolve_dataset_path(filename, search_dirs)
    if path is None:
        search_list = ", ".join(str(d) for d in (search_dirs or [DATA_DIR, ELLIPTIC_DIR]))
        raise FileNotFoundError(f"Missing {filename}. Looked in: {search_list}")
    return path
