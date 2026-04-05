from __future__ import annotations

import base64
import binascii
import re
import uuid
from pathlib import Path


DATA_IMAGE_RE = re.compile(r"^data:image/(?P<ext>[a-zA-Z0-9]+);base64,(?P<data>.+)$")


def save_base64_image(data: str, media_root: str = "media", subdir: str = "recipes") -> str:
    """
    Принимает строку вида:
    data:image/jpeg;base64,/9j/4AAQ...

    Сохраняет файл на диск и возвращает путь для БД, например:
    /media/recipes/550e8400-e29b-41d4-a716-446655440000.jpg
    """
    if not data:
        raise ValueError("Empty image data")

    match = DATA_IMAGE_RE.match(data.strip())
    if not match:
        raise ValueError("Invalid image format")

    ext = match.group("ext").lower()
    raw_data = match.group("data")

    ext_map = {
        "jpeg": "jpg",
        "jpg": "jpg",
        "png": "png",
        "gif": "gif",
        "webp": "webp",
    }

    if ext not in ext_map:
        raise ValueError("Unsupported image format")

    try:
        binary = base64.b64decode(raw_data, validate=True)
    except (binascii.Error, ValueError) as e:
        raise ValueError("Invalid base64 image data") from e

    filename = f"{uuid.uuid4()}.{ext_map[ext]}"
    dir_path = Path(media_root) / subdir
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / filename
    file_path.write_bytes(binary)

    return f"/media/{subdir}/{filename}"


def delete_image_file(image_path: str | None) -> None:
    """
    Удаляет файл, если он лежит внутри /media/.
    Ошибки удаления намеренно игнорируются.
    """
    if not image_path:
        return

    if not image_path.startswith("/media/"):
        return

    local_path = Path(image_path.lstrip("/"))
    try:
        if local_path.exists() and local_path.is_file():
            local_path.unlink()
    except OSError:
        pass