import re
import time
from findex2.index import build_index
from findex2.pipeline import iter_documents
from findex2.search import evaluate_query
from findex2.tokenizer import tokenize




def get_corpus_stream(dataset_path: str):
    docs = iter_documents(dataset_path)
    for numeric_id, doc in enumerate(docs):
        yield {
            "doc_id": numeric_id,

            "tokens": list(tokenize(doc.text)),
            "path": str(doc.path),
            "title": doc.doc_id,
        }


def benchmark(index):
    sorted_terms = sorted(index.postings.items(), key=lambda item: len(item[1]), reverse=True)

    most_common = [t[0] for t in sorted_terms[:2]]
    rarest = [t[0] for t in sorted_terms[-2:]]

    print(f"Найчастіші терми  : {most_common} (документів: {len(index.postings[most_common[0]])}, {len(index.postings[most_common[1]])})")
    print(f"Найрідкісніші терми: {rarest} (документів: {len(index.postings[rarest[0]])}, {len(index.postings[rarest[1]])})")
    print("-" * 75)

    queries = {
        "Common AND": f"{most_common[0]} AND {most_common[1]}",
        "Common OR":  f"{most_common[0]} OR {most_common[1]}",
        "Common NOT": f"{most_common[0]} NOT {most_common[1]}",
        "Rare AND":   f"{rarest[0]} AND {rarest[1]}",
        "Rare OR":    f"{rarest[0]} OR {rarest[1]}",
        "Rare NOT":   f"{rarest[0]} NOT {most_common[0]}",
    }

    print(f"{'Запит':<20} | {'Engine: MERGE (сек)':<20} | {'Engine: SET (сек)':<20} | ")
    print("-" * 75)

    iterations = 1000

    for name, q in queries.items():
        t0 = time.perf_counter()
        for _ in range(iterations):
            _ = evaluate_query(q, index, engine="merge")
        t_merge = time.perf_counter() - t0

        t0 = time.perf_counter()
        for _ in range(iterations):
            _ = evaluate_query(q, index, engine="set")
        t_set = time.perf_counter() - t0

        print(f"{name:<20} | {t_merge:.6f} s             | {t_set:.6f} s   ")


if __name__ == "__main__":
    dataset_path = "D:/pr/findex1/data"
    print("Побудова індексу для бенчмарку...")
    stream = get_corpus_stream(dataset_path)
    index = build_index(stream)
    benchmark(index)