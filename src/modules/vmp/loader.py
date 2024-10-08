from collections.abc import Mapping
import glob
from pathlib import Path
import re
import sys

from .models.config import Config
from .models.node import Node
from .models.image import DEFAULT_IMAGE_DIR, DEFAULT_IMAGE_TAG, Image
from .models.libvirt import (
    DEFAULT_NETWORK_NAME,
    DEFAULT_POOL_NAME,
    DEFAULT_POOL_PATH,
)
from .models.registry import Registry
from .models.vm import Vm
from .util import deep_format, get_by_name, strategic_merge, yaml_load


class Loader:
    def __init__(self, path: str | None = None):
        self.registry = load_registry(path) if path else load_registry_stdin()

    def load(self, name: str) -> Config:
        return load_config(self.registry, name)

    def load_image(self, image: str) -> Image:
        return load_image(self.registry, *split_image(image))

    def list(self) -> list[str]:
        return [vm.name for vm in self.registry.vms]


class RecursiveMapping(Mapping[str, str]):
    def __init__(
        self,
        vars: dict[str, str],
        memo: dict[str, str] | None = None,
        path: list[str] | None = None,
    ):
        super().__init__()
        self._vars = vars
        self._memo = memo if memo else {}
        self._path = path if path else []

    def __getitem__(self, key):
        if key in self._memo:
            return self._memo[key]
        if key in self._path:
            raise ValueError(f"The key '{key}' is circular recursion.")
        mapping = RecursiveMapping(self._vars, self._memo, self._path + [key])
        value = self._vars[key].format_map(mapping)
        self._memo[key] = value
        return value

    def __iter__(self):
        return iter(self._vars)

    def __len__(self):
        return len(self._vars)


def expand_vars(vars: dict[str, str]) -> dict[str, str]:
    mapping = RecursiveMapping(vars)
    return {key: mapping[key] for key in vars.keys()}


def load_config(
    registry: Registry,
    name: str,
) -> Config:
    vm = load_vm(registry, name)
    node = load_node(registry, vm.nodeName)
    image = load_image(registry, *split_image(vm.image))
    vars = expand_vars(load_vars(vm, node, image))
    return Config(
        vars=vars,
        vm=Vm(**deep_format(vm.dict(by_alias=True), vars)),
        node=node,
        image=image,
    )


def load_vars(vm: Vm, node: Node, image: Image) -> dict[str, str]:
    merged = (
        {
            "DEFAULT_IMAGE_DIR": DEFAULT_IMAGE_DIR,
            "DEFAULT_NETWORK_NAME": DEFAULT_NETWORK_NAME,
            "DEFAULT_POOL_NAME": DEFAULT_POOL_NAME,
            "DEFAULT_POOL_PATH": DEFAULT_POOL_PATH,
        }
        | node.vars
        | image.vars
        | vm.vars
        | {
            "IMAGE_FORMAT": image.format,
            "IMAGE_NAME": image.name,
            "IMAGE_TAG": image.tag,
            "IMAGE_URL": image.url,
            "IMAGE_VOLUME_NAME": image.volumeName,
            "NODE_NAME": node.name,
            "VM_NAME": vm.name,
        }
    )
    return dict(sorted(merged.items()))


def load_image(registry: Registry, name: str, tag) -> Image:
    image = get_by_name(registry.images, name)
    for x in image.tags:
        result = re.match(x.pattern, tag)
        if result is not None:
            archive = (
                Image.Archive(
                    type=x.archive.type,
                    path=(
                        x.archive.path.format(**result.groupdict())
                        if x.archive.path
                        else None
                    ),
                )
                if x.archive
                else x.archive
            )
            return Image(
                name=image.name,
                vars=image.vars | x.vars,
                tag=tag,
                url=x.url.format(**result.groupdict()),
                volumeName=x.volumeName.format(**result.groupdict()),
                format=x.format,
                archive=archive,
            )
    raise ValueError(f"could not resolve image (tag={tag})")


def load_node(registry: Registry, name: str) -> Node:
    return get_by_name(registry.nodes, name)


def load_registry(path: str) -> Registry:
    base = {}
    for file in sorted(glob.glob(path, recursive=True)):
        target = yaml_load(Path(file).read_text())
        base = strategic_merge(base, target)
    return Registry(**base)


def load_registry_stdin() -> Registry:
    return Registry(**yaml_load(sys.stdin.read()))


def load_vm(config: Config, name: str) -> Vm:
    def eval_template(target: Registry.Template) -> dict:
        if isinstance(target, Registry.TemplateWithMultipleInheritance):
            merged_dict = {}
            for base_name in target.templates:
                base = get_by_name(config.templates, base_name)
                base_dict = eval_template(base)
                merged_dict = strategic_merge(merged_dict, base_dict)
            return strategic_merge(merged_dict, target.dict(by_alias=True))
        elif isinstance(target, Registry.TemplateWithSingleInheritance):
            base = get_by_name(config.templates, target.template)
            base_dict = eval_template(base)
            return strategic_merge(base_dict, target.dict(by_alias=True))
        else:
            return target.dict(by_alias=True)

    template = get_by_name(config.vms, name)
    template_dict = eval_template(template)
    if "template" in template_dict:
        del template_dict["template"]
    if "templates" in template_dict:
        del template_dict["templates"]
    return Vm(**template_dict)


def split_image(image: str) -> [str, str]:
    return (image.split(":", maxsplit=1) + [DEFAULT_IMAGE_TAG])[0:2]
