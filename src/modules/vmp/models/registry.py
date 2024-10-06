from pydantic import BaseModel, Extra

from . import image, node, libvirt


class Registry(BaseModel, extra=Extra.forbid):
    class Image(BaseModel, extra=Extra.forbid):
        class Tag(BaseModel, extra=Extra.forbid):
            pattern: str
            vars: dict[str, str] = {}
            url: str
            volumeName: str
            format: str = libvirt.DEFAULT_FORMAT
            archive: image.Image.Archive | None = None

        name: str
        vars: dict[str, str] = {}
        tags: list[Tag]

    class Template(BaseModel, extra=Extra.allow):
        name: str

    class TemplateWithSingleInheritance(Template, extra=Extra.allow):
        name: str
        template: str

    class TemplateWithMultipleInheritance(Template, extra=Extra.allow):
        name: str
        templates: list[str]

    nodes: list[node.Node] = []
    images: list[Image] = []
    templates: list[
        TemplateWithMultipleInheritance
        | TemplateWithSingleInheritance
        | Template
    ] = []
    vms: list[
        TemplateWithMultipleInheritance
        | TemplateWithSingleInheritance
        | Template
    ] = []
