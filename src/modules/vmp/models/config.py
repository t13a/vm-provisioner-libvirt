from pydantic import BaseModel, Extra

from . import node, image, vm


class Config(BaseModel, extra=Extra.forbid):
    vars: dict[str, str] = {}
    image: image.Image
    node: node.Node
    vm: vm.Vm
