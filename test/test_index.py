import sys
import re
from pathlib import Path

from lab_02.index import build_index
from lab_02.pipeline import iter_documents


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def get_stream(dataset_path: str):
    docs = iter_documents(dataset_path)
    for numeric_id, doc in enumerate(docs):
        yield {
            "doc_id": numeric_id,
            "tokens": tokenize(doc.text),
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
            size += sys.getsizeof(p.positions)
    return size



def main():
    dataset_path = "D:/pr/findex1/data"

    if not Path(dataset_path).exists():
        print(f"Помилка: Папку '{dataset_path}' не знайдено.")
        return

    print("=== Перевірка M1: Побудова інвертованого індексу ===")


    index_no_pos = build_index(get_stream(dataset_path), with_positions=False)
    size_no_pos = sys.getsizeof(index_no_pos.postings)


    index_with_pos = build_index(get_stream(dataset_path), with_positions=True)
    size_with_pos = sys.getsizeof(index_with_pos.postings)


    total_no_pos = get_total_size(index_no_pos)
    total_with_pos = get_total_size(index_with_pos)

    print(f"Документів проіндексовано : {len(index_no_pos.doc_lengths)}")
    print(f"Унікальних термів        : {len(index_no_pos.postings)}")
    print("-" * 50)
    print(f"Повний розмір (без позицій) : {total_no_pos / (1024 * 1024):.2f} МБ")
    print(f"Повний розмір (з позиціями) : {total_with_pos / (1024 * 1024):.2f} МБ")

    if index_no_pos.postings:
        sample_term = list(index_no_pos.postings.keys())[0]
        print("\nПриклад терму:", sample_term)
        print("  Posting без позицій :", index_no_pos.postings[sample_term][0])
        print("  Posting з позиціями :", index_with_pos.postings[sample_term][0])


if __name__ == "__main__":
    main()