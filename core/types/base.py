# core/types/base.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class ModSource(ABC):
    def __init__(self, path: str):
        self.path = Path(path)

    @abstractmethod
    def load(self) -> List[str]:
        """Load and return mods"""
        raise NotImplementedError

    @abstractmethod
    def save(self, mods: List[str], out_path: str):
        """Save mods to output path"""
        raise NotImplementedError

    def get_raw_text(self) -> Optional[str]:
        """Optional raw text (used by SII)"""
        return None
