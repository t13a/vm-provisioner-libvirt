from typing import Literal

from pydantic import BaseModel, Extra

from . import libvirt

DEFAULT_IMAGE_DIR = ".images"
DEFAULT_IMAGE_TAG = "latest"


class Image(BaseModel, extra=Extra.forbid):
    class Archive(BaseModel, extra=Extra.forbid):
        type: Literal["7z"] | Literal["xz"]
        path: str | None = None

    name: str
    vars: dict[str, str] = {}
    tag: str = DEFAULT_IMAGE_TAG
    url: str
    volumeName: str
    format: str = libvirt.DEFAULT_FORMAT
    archive: Archive | None = None
