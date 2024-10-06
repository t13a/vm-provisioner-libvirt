from pathlib import Path
import re
import sys
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader

from . import abc
from .. import models, version
from ..models.config import Config
from ..models.libvirt import CreateDomainWithVirtInstall
from ..util import yaml_dump

NAME = "v1alpha1"


class V1Alpha1Generator(abc.GeneratorABC):
    def __init__(self, config: Config):
        self.context = V1Alpha1GeneratorContext(config)
        self.env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / NAME)
        )
        self.env.filters["regex_replace"] = regex_replace

    def gen(self, dir: Path):
        vm = self.context.config.vm
        self.write(dir / "Makefile")
        if vm.ssh and vm.ssh.password:
            self.write(dir / "sshpass")
        if vm.cloudInit:
            seed_dir = dir / f"{vm.cloudInit.noCloud.seed.path}.d"
            self.write(seed_dir / "meta-data")
            self.write(seed_dir / "user-data")
            if vm.cloudInit.noCloud.data.networkConfig:
                self.write(seed_dir / "network-config")
            if vm.cloudInit.noCloud.data.vendorData:
                self.write(seed_dir / "vendor-data")

    def render(self, template_file: str) -> str:
        template = self.env.get_template(template_file)
        return template.render(self.context)

    def write(self, file: Path, template_file: str | None = None) -> None:
        content = self.render(
            template_file if template_file else f"{file.name}.j2"
        )
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content)
        print(f"Generated {file}", file=sys.stderr)


class V1Alpha1GeneratorContext:
    def __init__(self, config: Config):
        self.config = config

        self.dict_merge = dict_merge
        self.isinstance = isinstance
        self.models = models
        self.sorted = sorted
        self.urlparse = urlparse
        self.yaml_dump = yaml_dump
        self.version = version.VERSION

    def __iter__(self):
        for name, value in vars(self).items():
            yield name, value
        for name in dir(self):
            if callable(getattr(self, name)) and not name.startswith("__"):
                yield name, getattr(self, name)

    def ssh_option_args(self) -> list[str]:
        args = []
        for k, v in sorted(self.config.vm.ssh.options.items()):
            if isinstance(v, list):
                args.append("-o")
                args.append("{}={}".format(k, ",".join(v)))
            elif isinstance(v, str):
                args.append("-o")
                args.append(f"{k}={v}")
        return args

    def virt_install_args(self) -> list[str]:
        args = []
        for k, v in sorted(self.config.vm.libvirt.domain.virtInstall.items()):
            if isinstance(v, list):
                for x in v:
                    assert isinstance(x, CreateDomainWithVirtInstall.Option)
                    options = []
                    if not isinstance(x.options, dict):
                        continue
                    for xk, xv in sorted(x.options.items()):
                        if isinstance(xv, bool) and xv:
                            options.append("{}".format(xk))
                        elif isinstance(xv, str):
                            options.append("{}={}".format(xk, xv))
                    if len(options) == 0:
                        continue
                    args.append("--{}={}".format(k, ",".join(options)))
            elif isinstance(v, bool) and v:
                args.append(f"--{k}")
            elif isinstance(v, str):
                args.append(f"--{k}={v}")
        return args


def dict_merge(*args: list[dict]) -> dict:
    result = {}
    for d in args:
        result.update(d)
    return result


def regex_replace(string, pattern, replace):
    return re.sub(pattern, replace, string)
