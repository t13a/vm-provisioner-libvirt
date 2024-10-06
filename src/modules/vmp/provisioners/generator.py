from pathlib import Path

from . import abc, v1alpha1
from ..models.config import Config


class Generator(abc.GeneratorABC):
    def __init__(self, config: Config):
        match config.vm.provisioner:
            case v1alpha1.NAME:
                self.impl = v1alpha1.V1Alpha1Generator(config)
            case _:
                raise ValueError(config.vm.provisioner)

    def gen(self, dir: Path) -> None:
        self.impl.gen(dir)
