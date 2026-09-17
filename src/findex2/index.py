from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class DocMeta:
    doc_id: int
    path: str
    title: str


@dataclass(frozen=True, slots=True)
class Posting:
    doc_id: int
    tf: int
    positions: tuple[int, ...] = ()


class InvertedIndex:
    def __init__(
        self,
        postings: dict[str, list[Posting]],
        doc_lengths: dict[int, int],
        doc_meta: dict[int, DocMeta],
    ):
        self.postings = postings
        self.doc_lengths = doc_lengths
        self.doc_meta = doc_meta

    def __len__(self) -> int:
        return len(self.postings)


def build_index(corpus: Iterable[dict], with_positions: bool = False) -> InvertedIndex:
    postings: dict[str, list[Posting]] = defaultdict(list)
    doc_lengths: dict[int, int] = {}
    doc_meta: dict[int, DocMeta] = {}

    for doc in corpus:
        doc_id: int = doc["doc_id"]
        tokens: list[str] = doc["tokens"]


        doc_meta[doc_id] = DocMeta(
            doc_id=doc_id,
            path=doc.get("path", ""),
            title=doc.get("title", ""),
        )
        doc_lengths[doc_id] = len(tokens)


        if with_positions:
            term_positions: dict[str, list[int]] = defaultdict(list)
            for pos, token in enumerate(tokens):
                term_positions[token].append(pos)

            for term, positions in term_positions.items():
                postings[term].append(
                    Posting(
                        doc_id=doc_id,
                        tf=len(positions),
                        positions=tuple(positions),
                    )
                )
        else:
            counts = Counter(tokens)
            for term, tf in counts.items():
                postings[term].append(Posting(doc_id=doc_id, tf=tf))

    return InvertedIndex(
        postings=dict(postings),
        doc_lengths=doc_lengths,
        doc_meta=doc_meta,
    )