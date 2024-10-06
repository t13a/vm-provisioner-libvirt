from abc import ABC, abstractmethod
from pathlib import Path


class GeneratorABC(ABC):
    @abstractmethod
    def gen(self, dir: Path) -> None:
        pass
