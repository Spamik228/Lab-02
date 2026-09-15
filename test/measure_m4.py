import os
import pickle
import re
import time
import tracemalloc
from pathlib import Path

from lab_02.pipeline import iter_documents
from lab_02.posting_variants import PostingArray, PostingPlain, PostingSlots


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def get_documents(dataset_path: Path):
    return list(iter_documents(dataset_path))


def build_variant_plain(docs):
    postings: dict[str, list[PostingPlain]] = {}
    doc_lengths: dict[int, int] = {}

    for doc_id, doc in enumerate(docs):
        tokens = tokenize(doc.text)
        doc_lengths[doc_id] = len(tokens)

        positions_map: dict[str, list[int]] = {}
        for pos, term in enumerate(tokens):
            positions_map.setdefault(term, []).append(pos)

        for term, pos_list in positions_map.items():
            p = PostingPlain(doc_id=doc_id, tf=len(pos_list), positions=tuple(pos_list))
            postings.setdefault(term, []).append(p)

    return postings, doc_lengths


def build_variant_slots(docs):
    postings: dict[str, list[PostingSlots]] = {}
    doc_lengths: dict[int, int] = {}

    for doc_id, doc in enumerate(docs):
        tokens = tokenize(doc.text)
        doc_lengths[doc_id] = len(tokens)

        positions_map: dict[str, list[int]] = {}
        for pos, term in enumerate(tokens):
            positions_map.setdefault(term, []).append(pos)

        for term, pos_list in positions_map.items():
            p = PostingSlots(doc_id=doc_id, tf=len(pos_list), positions=tuple(pos_list))
            postings.setdefault(term, []).append(p)

    return postings, doc_lengths


def build_variant_array(docs):
    postings: dict[str, PostingArray] = {}
    doc_lengths: dict[int, int] = {}

    for doc_id, doc in enumerate(docs):
        tokens = tokenize(doc.text)
        doc_lengths[doc_id] = len(tokens)

        positions_map: dict[str, list[int]] = {}
        for pos, term in enumerate(tokens):
            positions_map.setdefault(term, []).append(pos)

        for term, pos_list in positions_map.items():
            if term not in postings:
                postings[term] = PostingArray()
            postings[term].append(doc_id, len(pos_list), tuple(pos_list))

    return postings, doc_lengths


def run_benchmark():
    possible_paths = [
        Path("D:/pr/findex1/data"),
    ]

    dataset_path = next((p for p in possible_paths if p.exists() and p.is_dir()), None)
    if not dataset_path:
        print("Помилка: папка 'data' не знайдена.")
        return

    docs = get_documents(dataset_path)
    print(f"Зчитано {len(docs)} документів з {dataset_path.resolve()}\n")

    variants = [
        ("list[Posting] @dataclass", build_variant_plain),
        ("list[Posting] slots=True", build_variant_slots),
        ("array('I') pairs ", build_variant_array),
    ]

    results = []

    for name, builder_func in variants:

        tracemalloc.start()
        t0 = time.perf_counter()
        index_data, _ = builder_func(docs)
        _ = time.perf_counter() - t0
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak_bytes / (1024 * 1024)


        out_path = f"index_m4_{name.split()[0]}.bin"
        with open(out_path, "wb") as f:
            pickle.dump(index_data, f, protocol=pickle.HIGHEST_PROTOCOL)

        file_size_mb = os.path.getsize(out_path) / (1024 * 1024)


        t_load_start = time.perf_counter()
        with open(out_path, "rb") as f:
            _ = pickle.load(f)
        load_time_s = time.perf_counter() - t_load_start


        if os.path.exists(out_path):
            os.remove(out_path)

        results.append(
            {
                "representation": name,
                "peak_memory": peak_mb,
                "file_size": file_size_mb,
                "load_time": load_time_s,
            }
        )


    print("=" * 85)
    print(
        f"{'Postings representation':<35} | {'Peak memory (build)':<20} | {'Index file size':<16} | {'Load time':<10}"
    )
    print("-" * 85)
    for res in results:
        print(
            f"{res['representation']:<35} | "
            f"{res['peak_memory']:<17.2f} MB | "
            f"{res['file_size']:<13.2f} MB | "
            f"{res['load_time']:<8.4f} s"
        )
    print("=" * 85)


if __name__ == "__main__":
    run_benchmark()