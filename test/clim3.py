import argparse
import re
import time
import tracemalloc
from pathlib import Path
from findex2.tokenizer import tokenize
from findex2.index import build_index
from findex2.pipeline import iter_documents
from findex2.search import evaluate_query
from findex2.store import load, save




def get_stream(dataset_path: Path):
    docs = iter_documents(dataset_path)
    for numeric_id, doc in enumerate(docs):
        yield {
            "doc_id": numeric_id,
            "tokens": list(tokenize(doc.text)),
            "path": str(doc.path),
            "title": doc.doc_id,
        }


def handle_index(args):
    data_path = Path(args.data_dir)
    if not data_path.exists():
        print(f"Помилка: Шлях '{data_path}' не існує.")
        return

    tracemalloc.start()
    t_start = time.perf_counter()

    print(f"Зчитування даних з '{data_path}' та побудова індексу...")
    stream = get_stream(data_path)
    index = build_index(stream)

    save(index, args.out, fmt=args.format)

    t_elapsed = time.perf_counter() - t_start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"\n[УСПІХ] Індекс побудовано та збережено у '{args.out}'.")
    print(f"Elapsed time : {t_elapsed:.4f} секунд")
    print(f"Peak memory  : {peak_bytes / (1024 * 1024):.2f} MB")


def handle_search(args):
    index_path = Path(args.index_path)
    if not index_path.exists():
        print(f"Помилка: Файл індексу '{index_path}' не знайдено.")
        return

    tracemalloc.start()
    t_start = time.perf_counter()

    index = load(index_path, fmt=args.format)
    results = evaluate_query(args.query, index, engine=args.engine)

    t_elapsed = time.perf_counter() - t_start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"\nЗнайдено документів: {len(results)}")
    for doc_id in results[:20]:
        meta = index.doc_meta.get(doc_id)
        title = meta.title if meta else f"Doc #{doc_id}"
        print(f"  • [ID: {doc_id}] {title}")

    if len(results) > 20:
        print(f"  ... та ще {len(results) - 20} результатів.")

    print("\n--- Performance Metrics ---")
    print(f"Elapsed time : {t_elapsed:.4f} секунд")
    print(f"Peak memory  : {peak_bytes / (1024 * 1024):.2f} MB")


def main():
    parser = argparse.ArgumentParser(
        description="CLI-інструмент для побудови індексу та пошуку (Findex)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)


    parser_index = subparsers.add_parser("index", help="Побудувати та зберегти індекс.")
    parser_index.add_argument("data_dir", type=str, help="Шлях до корпусу файлів")
    parser_index.add_argument("--out", type=str, default="index.bin", help="Шлях вихідного файлу")
    parser_index.add_argument("--format", type=str, choices=["pickle", "json"], default="pickle")
    parser_index.set_defaults(func=handle_index)


    parser_search = subparsers.add_parser("search", help="Завантажити індекс та виконати пошук.")
    parser_search.add_argument("index_path", type=str, help="Шлях до файлу індексу")
    parser_search.add_argument("query", type=str, help="Пошуковий запит")
    parser_search.add_argument("--engine", type=str, choices=["merge", "set"], default="merge")
    parser_search.add_argument("--format", type=str, choices=["pickle", "json"], default="pickle")
    parser_search.set_defaults(func=handle_search)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()