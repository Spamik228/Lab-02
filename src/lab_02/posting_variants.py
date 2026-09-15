from array import array
from dataclasses import dataclass
from typing import NamedTuple, Any


# Стандартний dataclass (кожен об'єкт має свій __dict__)
@dataclass
class PostingPlain:
    doc_id: int
    tf: int
    positions: tuple[int, ...]


# Dataclass з підтримкою slots=True (без __dict__)
@dataclass(slots=True)
class PostingSlots:
    doc_id: int
    tf: int
    positions: tuple[int, ...]


# Масиви array('I') без об'єктів на окремий постинг
class PostingArray:

    __slots__ = ("doc_ids", "tfs", "positions", "offsets")

    def __init__(self):
        self.doc_ids = array("I")
        self.tfs = array("I")
        self.positions = array("I")
        self.offsets = array("I")  # Початок і кінець позицій для кожного постингу

    def append(self, doc_id: int, tf: int, positions: tuple[int, ...]) -> None:
        self.doc_ids.append(doc_id)
        self.tfs.append(tf)
        start_idx = len(self.positions)
        self.positions.extend(positions)
        end_idx = len(self.positions)
        self.offsets.append(start_idx)
        self.offsets.append(end_idx)