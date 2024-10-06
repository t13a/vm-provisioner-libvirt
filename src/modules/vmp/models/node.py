from pydantic import BaseModel, Extra

from . import libvirt


class Node(BaseModel, extra=Extra.forbid):
    class Libvirt(BaseModel, extra=Extra.forbid):
        connection: libvirt.Connection
        # connection: libvirt.LocalConnection | libvirt.SshConnection

    name: str
    vars: dict[str, str] = {}
    libvirt: Libvirt
