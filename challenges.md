# ragforensics: challenges and risks

The hard problems in this project, why each is hard, and how it is being handled. Status values: **Open**, **De-risked** (evidence it is solvable, not finished), **Solved**, **Accepted** (known limitation, documented).

| ID | Challenge | Phase | Status |
|---|---|---|---|
| C1 | Exact HNSW replay across metrics, ties and library versions | 1 | De-risked |
| C2 | hnswlib graph extraction | 1 | Open |
| C3 | Replaying the user's own stages without drift | 1–2 | Open |
| C4 | Gold as a span: locating evidence text in parsed documents | 1–2 | Open |
| C5 | Chunking blame (split, dilution) and the cost of re-chunking | 2–3 | Open |
| C6 | Evidence for embedding mismatch (the most common real miss) | 2 | Open |
| C7 | Filtered ANN (post-filter starvation, filter/graph interaction) | 2, 6 | Open |
| C8 | Defining "smallest" repair across unlike knobs | 3 | Open |
| C9 | Side-effect checks at corpus scale | 3 | Open |
| C10 | Evaluation circularity (planted bugs we already know how to find) | 2, 7 | Open |
| C11 | Synthetic questions that really have one gold answer | 4 | Open |
| C12 | PDF parsing and tables (FinanceBench) | 2 | Open |
| C13 | Reranker and GPU non-determinism | 2 | Open |
| C14 | Vector DBs that hide their graph | 6 | Open |
| C15 | Scoop risk | all | Open |
| C16 | Dataset licensing (FinanceBench is CC-BY-NC) | 2 | Accepted |

## Details

### C1. Exact HNSW replay across metrics, ties and library versions
- **Why hard:** the replay must equal FAISS's own output, or every explanation is suspect. FAISS computes distances with SIMD kernels whose float rounding can differ from numpy, its candidate heap has tie-breaking quirks, and internals change between versions.
- **Evidence so far:** spike E1 (`report.md`) matched FAISS 1.15.1 on 900/900 queries (L2, flat storage).
- **Plan:** property tests over random datasets, metrics (L2, inner product, cosine), efSearch values, and planted exact ties; pin the FAISS version and run fidelity tests in CI; if float rounding ever flips an ordering, compute distances through FAISS itself instead of numpy.

### C2. hnswlib graph extraction
- **Why hard:** hnswlib's Python binding does not document graph access. Pickled state exposes the raw level-0 data and link lists as bytes, which must be decoded by hand, and the search loop differs from FAISS's.
- **Plan:** decode the pickled state, write a separate replayer, hold it to the same fidelity bar as FAISS. Use `chroma-hnswlib` 0.7.6 (the only build with Windows wheels; Python 3.11).

### C3. Replaying the user's own stages without drift
- **Why hard:** re-implementing a user's filter, fusion, reranker or packer inside ragforensics drifts from their real code.
- **Plan:** adapters expose each stage as a callable; ragforensics re-invokes it with the gold candidate injected. Candidate-generating stages (ANN, BM25) report gold's exact score and rank against the stage cutoff. The trace must record enough inputs (query, config, upstream candidates) to re-invoke each stage deterministically.

### C4. Gold as a span
- **Why hard:** labels name a document or quote evidence text that may not match the parsed text exactly (whitespace, hyphenation, PDF extraction errors, table flattening).
- **Plan:** exact match, then normalized match, then fuzzy alignment with a reported confidence. A failed alignment is itself evidence of a parse-stage loss.

### C5. Chunking blame and re-chunking cost
- **Why hard:** "chunking lost it" is a counterfactual: the right chunk never existed. Testing a different chunking means re-embedding.
- **Plan:** classify as split (span crosses a boundary) or dilution (query similarity of the span alone vs its chunk). Re-chunk and re-embed only the affected document, with a content-hash embedding cache.

### C6. Evidence for embedding mismatch
- **Why hard:** when the gold's exact rank is 87 there is no "kept set" to fall out of, and "the model didn't think it was similar" is not an explanation.
- **Plan:** report exact rank, the similarity gap to the k-th result, lexical overlap and missing query terms, and whether a query rewrite or hybrid weight rescues it, all verified by replay.

### C7. Filtered ANN
- **Why hard:** a filter applied after the ANN search can leave too few results (pgvector's own docs: a 10% filter with ef_search 40 returns about 4 rows); a filter applied during the search can disconnect the graph.
- **Plan:** replay the walk with the filter, count how many filtered candidates were reachable, and test the counterfactuals (higher ef, pre-filter, iterative scan).

### C8. Defining "smallest" repair
- **Why hard:** efSearch, top-k, chunk size and fusion weight have no common unit.
- **Plan:** an explicit cost model (added latency, re-embedding volume, index rebuild, chance of breaking other queries); search cheapest-first. The formal framing follows He & Lo's minimal query refinement for why-not top-k queries.

### C9. Side-effect checks at corpus scale
- **Why hard:** each candidate repair must be re-checked against the whole eval set.
- **Plan:** partial replay of only the affected stages, caching, and early stopping once a repair breaks more queries than it fixes.

### C10. Evaluation circularity
- **Why hard:** if we plant only the bugs we know how to detect, ≥90% accuracy means little.
- **Plan:** add a blind random-perturbation benchmark (random config changes, verdicts checked against exhaustive replay) and report results on real misses separately.

### C11. Synthetic questions with one gold answer
- **Why hard:** LLM-written questions are often answerable from several chunks, so the "gold" is not unique.
- **Plan:** an ambiguity filter (does the answer appear in, or get entailed by, other chunks?) and report how many questions it rejects.

### C12. PDF parsing and tables
- **Why hard:** 10-K tables flatten badly, and parse errors become hidden losses that look like chunking or embedding failures.
- **Plan:** treat parsing as a stage with its own verdict, and keep the parser swappable.

### C13. Reranker and GPU non-determinism
- **Why hard:** cross-encoder scores can shift slightly with batch composition, padding or GPU kernels, so "replay equals production" may fail at the last decimal place.
- **Plan:** measure the drift, use a documented tolerance, and flag verdicts whose margin is inside the tolerance.

### C14. Vector DBs that hide their graph
- **Why hard:** pgvector, Qdrant and Pinecone don't expose HNSW internals.
- **Plan:** tier-1 diagnosis (ANN rank vs exact rank) for every backend; graph-level diagnosis only where the graph is available.

### C15. Scoop risk
- **Why hard:** RAGFlip, FaulTrace-RAG and a now-deleted `rag-regression-debugger` show others are working nearby.
- **Plan:** publish the repo and a short problem write-up early; differentiate on evidence, replay fidelity and costed repairs.

### C16. Dataset licensing
- FinanceBench is CC-BY-NC-4.0. We ship a download script, never the data, and say so in the README.
