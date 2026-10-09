# ragforensics: challenges log

Technical and research problems actually hit while building ragforensics, and how each was handled. Newest first. Only problems that matter to the project itself (its code, dependencies, algorithms, data, evaluation or positioning) belong here, not tooling or session friction. Expected risks that haven't happened yet live in the "Risks" section of `report.md`.

Each entry records what happened, how it showed up, what fixed it, and whether it is resolved.

---

### 2026-10-10. hnswlib does not install on Windows
- **What happened:** `hnswlib` 0.8.0 ships no Windows wheels, and building it from source needs a C++ compiler (MSVC). The install failed on a stock Windows machine. The only prebuilt alternative, `chroma-hnswlib` 0.7.6, has Windows wheels only up to Python 3.11 (a first attempt failed because the environment silently used 3.12).
- **Fix:** use `chroma-hnswlib` 0.7.6 and pin the project to Python 3.11.
- **Status:** worked around, with a follow-up. As a hard dependency, this would stop Windows users on Python 3.12+ from installing ragforensics at all. Before release, move hnswlib into an optional extra (`ragforensics[hnswlib]`) so the core package installs anywhere and only the hnswlib replayer needs it.

### 2026-10-09. Matching FAISS's HNSW search loop exactly
- **What happened:** a replay that only "looks like HNSW" would not reproduce FAISS's results; the details of FAISS's level-0 search decide which nodes are visited. The ones that mattered:
  - The candidate list is a fixed-size array (`MinimaxHeap`). When it is full, the farthest entry is evicted, and a new candidate no closer than that is dropped.
  - Popped candidates stay in the array (marked invalid), and the stopping rule `count_below(d)` counts them too: the search stops once at least efSearch entries in the array, including popped ones, are closer than the candidate just popped.
  - Upper levels use a plain greedy descent that scans the whole neighbour list of the current node before moving.
- **Fix:** mirror these rules exactly. The spike matched FAISS 1.15.1 on 900/900 queries, set and order (`report.md`, E1).
- **Status:** resolved for L2 with flat storage. Inner product, cosine and distance ties are still untested, and FAISS is pinned `<1.16` because these internals can change between versions.

### 2026-10-09. FAISS graph arrays have mixed integer types
- **What happened:** the first replay run failed with `TypeError: slice indices must be integers`. `hnsw.offsets` comes back as unsigned 64-bit and `cum_nneighbor_per_level` as 32-bit; numpy promotes their sum to a float.
- **Fix:** convert both to plain Python `int` before slicing.
- **Status:** resolved; the Phase 1 replayer must do the same.

### 2026-10-09. Prior-art claims in the brief that could not be verified
- **What happened:** the brief cites "Ferryte (PyPI)" as related work; it could not be found on PyPI or the web. A search result described a close competitor, `rag-regression-debugger` (said to record whether evidence was lost at indexing, retrieval, ranking or reranking), but its GitHub repo returned 404.
- **Handling:** Ferryte is left out of the prior-work table. `rag-regression-debugger` is noted only as a scoop-risk signal, since its claims can't be checked.
- **Status:** resolved (documented). Re-check before the paper write-up.
