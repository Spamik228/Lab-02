import os
import re
import time
from pathlib import Path

from lab_02.index import build_index
from lab_02.pipeline import iter_documents
from lab_02.store import load, save


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def get_stream(dataset_path: Path):
    docs = iter_documents(dataset_path)
    for numeric_id, doc in enumerate(docs):
        yield {
            "doc_id": numeric_id,
            "tokens": tokenize(doc.text),
            "path": str(doc.path),
            "title": doc.doc_id,
        }


def measure_formats():
    #
    possible_paths = [
        Path("D:/pr/findex1/data"),

    ]

    dataset_path = None
    for p in possible_paths:
        if p.exists() and p.is_dir():
            dataset_path = p
            break

    if not dataset_path:
        print("Помилка: Папку 'data' не знайдено за жодним із можливих шляхів.")
        return

    print(f"Зчитування даних з: {dataset_path.resolve()}")
    print("Побудова індексу в пам'яті...")

    stream = get_stream(dataset_path)
    index = build_index(stream)

    if not index.doc_lengths:
        print("Попередження: Не знайдено жодного .txt файлу у папці data.")
        return

    formats = ["pickle", "json"]
    results = {}

    for fmt in formats:
        out_file = f"index.{fmt}"


        t0 = time.perf_counter()
        save(index, out_file, fmt=fmt)
        save_time = time.perf_counter() - t0

        file_size = os.path.getsize(out_file) / (1024 * 1024)


        t0 = time.perf_counter()
        _ = load(out_file, fmt=fmt)
        load_time = time.perf_counter() - t0

        results[fmt] = {
            "file_size": file_size,
            "save_time": save_time,
            "load_time": load_time,
        }


        if Path(out_file).exists():
            os.remove(out_file)

    print("\n" + "=" * 65)
    print(f"{'Format':<10} | {'File Size (MB)':<15} | {'Save Time (s)':<15} | {'Load Time (s)':<15}")
    print("-" * 65)
    for fmt, metrics in results.items():
        print(
            f"{fmt:<10} | "
            f"{metrics['file_size']:<15.2f} | "
            f"{metrics['save_time']:<15.4f} | "
            f"{metrics['load_time']:<15.4f}"
        )
    print("=" * 65)


if __name__ == "__main__":
    measure_formats()