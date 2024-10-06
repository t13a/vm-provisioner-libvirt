from pydantic import BaseModel, Extra

from . import cloud_init, libvirt


class Vm(BaseModel, extra=Extra.forbid):
    class Libvirt(BaseModel, extra=Extra.forbid):
        domain: libvirt.CreateDomainWithVirtInstall
        pools: list[libvirt.DirectoryPool] = []
        volumes: list[
            libvirt.CreateVolumeFromBlank
            | libvirt.CreateVolumeFromBackingVolume
            | libvirt.CreateVolumeFromUploadFile
        ] = []

    class CloudInit(BaseModel, extra=Extra.forbid):
        noCloud: cloud_init.NoCloud

    class Ssh(BaseModel, extra=Extra.forbid):
        user: str = None
        host: str = None
        password: str = None
        options: dict[str, list[str] | str | None] = {}

    name: str
    nodeName: str
    image: str
    vars: dict[str, str] = {}
    provisioner: str
    libvirt: Libvirt
    cloudInit: CloudInit | None = None
    ssh: Ssh | None = None
