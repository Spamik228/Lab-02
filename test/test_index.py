import sys
from pathlib import Path

from findex2.index import build_index
from findex2.pipeline import iter_documents
from findex2.tokenizer import tokenize


def get_stream(dataset_path: str):
    docs = iter_documents(dataset_path)
    for numeric_id, doc in enumerate(docs):
        yield {
            "doc_id": numeric_id,
            "tokens": list(tokenize(doc.text)),
            "path": str(doc.path),
            "title": doc.doc_id,
        }


def get_total_size(index) -> int:
    size = sys.getsizeof(index.postings)


    for term, posting_list in index.postings.items():
        size += sys.getsizeof(term)
        size += sys.getsizeof(posting_list)
        for p in posting_list:
            size += sys.getsizeof(p)
            if p.positions:
                size += sys.getsizeof(p.positions)
                for pos in p.positions:
                    size += sys.getsizeof(pos)


    size += sys.getsizeof(index.doc_lengths)
    for doc_id, length in index.doc_lengths.items():
        size += sys.getsizeof(doc_id)
        size += sys.getsizeof(length)

    size += sys.getsizeof(index.doc_meta)
    for doc_id, meta in index.doc_meta.items():
        size += sys.getsizeof(doc_id)
        size += sys.getsizeof(meta)
        size += sys.getsizeof(meta.path)
        size += sys.getsizeof(meta.title)

    return size


def main():
    dataset_path = "D:/pr/findex1/data"

    if not Path(dataset_path).exists():
        print(f"Помилка: Папку '{dataset_path}' не знайдено.")
        return

    print("=== Перевірка M1: Побудова інвертованого індексу ===")

    index_no_pos = build_index(get_stream(dataset_path), with_positions=False)
    index_with_pos = build_index(get_stream(dataset_path), with_positions=True)

    total_no_pos = get_total_size(index_no_pos)
    total_with_pos = get_total_size(index_with_pos)

    print(f"Документів проіндексовано : {len(index_no_pos.doc_lengths)}")
    print(f"Унікальних термів        : {len(index_no_pos.postings)}")
    print("-" * 50)
    print(
        f"Повний розмір (без позицій) : {total_no_pos / (1024 * 1024):.2f} МБ"
    )
    print(
        f"Повний розмір (з позиціями) : {total_with_pos / (1024 * 1024):.2f} МБ"
    )

    if total_no_pos > 0:
        overhead = ((total_with_pos - total_no_pos) / total_no_pos) * 100
        print(f"Оверхед пам'яті за позиції  : +{overhead:.1f}%")

    if index_no_pos.postings:
        sample_term = list(index_no_pos.postings.keys())[0]
        print("\nПриклад терму:", sample_term)
        print("  Posting без позицій :", index_no_pos.postings[sample_term][0])
        print("  Posting з позиціями :", index_with_pos.postings[sample_term][0])


if __name__ == "__main__":
    main()