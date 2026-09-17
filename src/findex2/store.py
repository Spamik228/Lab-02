import json
import pickle
from pathlib import Path
from findex2.index import DocMeta, InvertedIndex, Posting


# WARNING / SECURITY NOTE:
# Never use `pickle.load()` on untrusted or untrusted-source files!
# Pickle allows execution of arbitrary Python code during deserialization
# (via __reduce__ exploit vectors). An attacker could construct a malicious
# file that executes shell commands upon loading.


def save_pickle(index: InvertedIndex, path: Path | str) -> None:
    with open(path, "wb") as f:
        pickle.dump(index, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(path: Path | str) -> InvertedIndex:
    with open(path, "rb") as f:
        return pickle.load(f)


def save_json(index: InvertedIndex, path: Path | str) -> None:
    data = {
        "doc_lengths": index.doc_lengths,
        "doc_meta": {
            str(k): {"doc_id": v.doc_id, "path": v.path, "title": v.title}
            for k, v in index.doc_meta.items()
        },
        "postings": {
            term: [
                {"doc_id": p.doc_id, "tf": p.tf, "positions": list(p.positions)}
                for p in posting_list
            ]
            for term, posting_list in index.postings.items()
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def load_json(path: Path | str) -> InvertedIndex:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc_lengths = {int(k): v for k, v in data["doc_lengths"].items()}
    doc_meta = {
        int(k): DocMeta(doc_id=v["doc_id"], path=v["path"], title=v["title"])
        for k, v in data["doc_meta"].items()
    }
    postings = {
        term: [
            Posting(doc_id=p["doc_id"], tf=p["tf"], positions=tuple(p["positions"]))
            for p in posting_list
        ]
        for term, posting_list in data["postings"].items()
    }

    return InvertedIndex(
        postings=postings,
        doc_lengths=doc_lengths,
        doc_meta=doc_meta,
    )


def save(index: InvertedIndex, path: Path | str, fmt: str = "pickle") -> None:
    if fmt == "pickle":
        save_pickle(index, path)
    elif fmt == "json":
        save_json(index, path)
    else:
        raise ValueError(f"Unknown format: {fmt}")


def load(path: Path | str, fmt: str = "pickle") -> InvertedIndex:
    if fmt == "pickle":
        return load_pickle(path)
    elif fmt == "json":
        return load_json(path)
    else:
        raise ValueError(f"Unknown format: {fmt}")