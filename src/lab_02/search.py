import argparse
import time
from typing import Sequence
from lab_02.index import InvertedIndex, Posting


# ==========================================
# 1. Algorithmic Implementations (Two-Pointer)
# ==========================================

def intersect_postings_merge(p1: Sequence[Posting], p2: Sequence[Posting]) -> list[int]:

    res = []
    i = j = 0
    len1, len2 = len(p1), len(p2)
    while i < len1 and j < len2:
        id1, id2 = p1[i].doc_id, p2[j].doc_id
        if id1 == id2:
            res.append(id1)
            i += 1
            j += 1
        elif id1 < id2:
            i += 1
        else:
            j += 1
    return res


def union_postings_merge(p1: Sequence[Posting], p2: Sequence[Posting]) -> list[int]:

    res = []
    i = j = 0
    len1, len2 = len(p1), len(p2)
    while i < len1 and j < len2:
        id1, id2 = p1[i].doc_id, p2[j].doc_id
        if id1 == id2:
            res.append(id1)
            i += 1
            j += 1
        elif id1 < id2:
            res.append(id1)
            i += 1
        else:
            res.append(id2)
            j += 1

    while i < len1:
        res.append(p1[i].doc_id)
        i += 1
    while j < len2:
        res.append(p2[j].doc_id)
        j += 1
    return res


def difference_postings_merge(p1: Sequence[Posting], p2: Sequence[Posting]) -> list[int]:

    res = []
    i = j = 0
    len1, len2 = len(p1), len(p2)
    while i < len1 and j < len2:
        id1, id2 = p1[i].doc_id, p2[j].doc_id
        if id1 == id2:
            i += 1
            j += 1
        elif id1 < id2:
            res.append(id1)
            i += 1
        else:
            j += 1

    while i < len1:
        res.append(p1[i].doc_id)
        i += 1
    return res


# ==========================================
# 2. Python Set Implementations
# ==========================================

def intersect_postings_set(p1: Sequence[Posting], p2: Sequence[Posting]) -> list[int]:
    s1 = {p.doc_id for p in p1}
    s2 = {p.doc_id for p in p2}
    return sorted(list(s1 & s2))


def union_postings_set(p1: Sequence[Posting], p2: Sequence[Posting]) -> list[int]:
    s1 = {p.doc_id for p in p1}
    s2 = {p.doc_id for p in p2}
    return sorted(list(s1 | s2))


def difference_postings_set(p1: Sequence[Posting], p2: Sequence[Posting]) -> list[int]:
    s1 = {p.doc_id for p in p1}
    s2 = {p.doc_id for p in p2}
    return sorted(list(s1 - s2))


# ==========================================
# 3. Simple Left-to-Right Query Evaluator
# ==========================================

def evaluate_query(query: str, index: InvertedIndex, engine: str = "merge") -> list[int]:

    tokens = query.casefold().split()
    if not tokens:
        return []


    if engine == "merge":
        op_and, op_or, op_not = intersect_postings_merge, union_postings_merge, difference_postings_merge
    else:
        op_and, op_or, op_not = intersect_postings_set, union_postings_set, difference_postings_set


    def term_postings(term: str) -> list[Posting]:
        return index.postings.get(term, [])


    first_term = tokens[0]
    current_postings = term_postings(first_term)
    current_doc_ids = [p.doc_id for p in current_postings]

    i = 1
    while i < len(tokens):
        op = "AND"
        token = tokens[i]

        if token in ("and", "or", "not"):
            op = token.upper()
            i += 1
            if i >= len(tokens):
                break
            target_term = tokens[i]
        else:
            target_term = token

        target_postings = term_postings(target_term)


        current_as_postings = [Posting(doc_id=d, tf=1) for d in current_doc_ids]

        if op == "AND":
            current_doc_ids = op_and(current_as_postings, target_postings)
        elif op == "OR":
            current_doc_ids = op_or(current_as_postings, target_postings)
        elif op == "NOT":
            current_doc_ids = op_not(current_as_postings, target_postings)

        i += 1

    return current_doc_ids