# ragforensics

**Why wasn't this retrieved?** Given a question and the passage that should have reached the LLM, ragforensics follows that passage through every stage of a retrieval pipeline (parsing, chunking, embedding, ANN search, filters, keyword search, fusion, reranking, context packing). It reports which stages would and would not have kept it, with evidence, and proposes the cheapest change that brings it back, verified by replay.

> **Status: pre-alpha, under active development.** Nothing is usable yet. See [report.md](report.md) for progress and [challenges.md](challenges.md) for the open problems.

## What makes it different

- **Why-not, not why.** Existing RAG debuggers explain what *was* retrieved. ragforensics explains what was *not*.
- **Evidence, not guesses.** Every verdict carries ranks, scores, cutoffs, or the HNSW nodes the search visited, checked against exact brute-force search.
- **Faithful replay.** For FAISS and hnswlib, the HNSW graph walk is replayed step by step and must return exactly what the library returns.
- **Verified, costed repairs.** Each suggested fix is re-run, priced (latency, re-embedding, index rebuild), and checked for queries it would break.

## Planned support

- ANN backends: FAISS and hnswlib (graph-level), then pgvector (rank-level).
- Datasets for demos and evaluation: BEIR SciFact and FinanceBench.
- Local models by default (sentence-transformers, Ollama); API models optional.

## Development

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11.

```
uv sync
uv run pytest
```

## License

Apache-2.0. See [LICENSE](LICENSE).
