from typing import Literal

from pydantic import BaseModel, Extra, StrictBool

DEFAULT_NETWORK_NAME = "default"
DEFAULT_POOL_NAME = "default"
DEFAULT_POOL_PATH = "/var/lib/libvirt/images"
DEFAULT_FORMAT = "qcow2"


class Connection(BaseModel, extra=Extra.forbid):
    uri: str


class Domain(BaseModel, extra=Extra.forbid):
    name: str


class CreateDomainWithVirtInstall(Domain, extra=Extra.forbid):
    class Option(BaseModel, extra=Extra.forbid):
        name: str
        options: dict[str, StrictBool | str | None] | None

    virtInstall: dict[str, list[Option] | StrictBool | str | None] = {}


class Pool(BaseModel, extra=Extra.forbid):
    name: str


class DirectoryPool(Pool, extra=Extra.forbid):
    class Directory(BaseModel, extra=Extra.forbid):
        path: str

    deletionPolicy: Literal["Delete"] | Literal["Retain"] = "Delete"
    directory: Directory


class Volume(BaseModel, extra=Extra.forbid):
    name: str
    poolName: str
    format: str = DEFAULT_FORMAT


class CreateVolume(Volume, extra=Extra.forbid):
    deletionPolicy: Literal["Delete"] | Literal["Retain"] = "Delete"


class CreateVolumeFromBlank(CreateVolume, extra=Extra.forbid):
    capacity: str


class CreateVolumeFromBackingVolume(CreateVolume, extra=Extra.forbid):
    capacity: str | None = None
    backingVolume: Volume


class CreateVolumeFromUploadFile(CreateVolume, extra=Extra.forbid):
    class UploadFile(BaseModel, extra=Extra.forbid):
        path: str

    capacity: str | None = None
    uploadFile: UploadFile
