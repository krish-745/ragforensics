# ragforensics: project report

Living status document. Newest entries go at the top of each log. Problems actually hit while building are logged in `challenges.md`; expected risks are listed under "Risks" below.

## Status

| Phase | State | Exit check |
|---|---|---|
| 0. Setup | Done (2026-10-10) | Repo skeleton, license, tests run |
| 1. Trace and replay foundation | Next | `ragforensics explain` prints a survival vector on SciFact |
| 2. Blame | Not started | ≥90% correct verdicts on planted and blind-perturbation bugs |
| 3. Repair | Not started | Verified, costed repairs for most planted bugs |
| 4. Corpus mode | Not started | Funnel and audit run on a full dataset |
| 5. Web UI | Not started | End-to-end demo in the browser |
| 6. pgvector + LlamaIndex | Not started | Tier-1 diagnosis on pgvector |
| 7. Evaluation and release | Not started | Paper-style write-up, PyPI release |

## Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-10-10 | Name `ragforensics` (GitHub + PyPI) | Original name `whynot` is taken on PyPI; user picked from available candidates |
| 2026-10-10 | Apache-2.0 license | Permissive, includes a patent grant, common for ML tooling |
| 2026-10-10 | Python 3.11 | `chroma-hnswlib` has Windows wheels only up to cp311; plain `hnswlib` 0.8.0 has no Windows wheels and fails to build without MSVC |
| 2026-10-10 | Datasets: SciFact + FinanceBench | SciFact is small and standard (fidelity tests). FinanceBench has long PDFs, tables and company/year/doc-type metadata, so chunking, parsing and filter failures can occur naturally; its evidence text gives span-level gold |
| 2026-10-10 | Reframed design (span gold, stage DAG, survival vector via gold injection, two-tier ANN, filtered ANN as headline, costed repairs) | Idea review: re-implementing user stages drifts; most real DBs hide their graph; first-loss-only blame hides interactions; ANN is a minority cause of real misses |
| 2026-10-10 | Phases without deadlines; user reviews at the end of each phase | User has no deadline; wants a middle-ground involvement |
| 2026-10-10 | Local Ollama default, API LLMs swappable | Free, local by default |

## Experiments and results

### E1. Pure-Python replay of FAISS HNSW search (2026-10-09)

A ~60-line Python re-implementation of FAISS 1.15.1 `IndexHNSWFlat` search (greedy descent on upper levels, bounded candidate heap with `check_relative_distance` on level 0), reading the graph from `hnsw.neighbors`, `offsets`, `cum_nneighbor_per_level` and `entry_point`.

Setup: 20,000 random Gaussian vectors, d=64, M=16, efConstruction=40, 300 queries, k=10, L2.

| efSearch | Replay == FAISS (set) | Replay == FAISS (order) | FAISS recall@10 | Mean distance evaluations |
|---|---|---|---|---|
| 10 | 300/300 | 300/300 | 0.322 | 372 |
| 16 | 300/300 | 300/300 | 0.424 | 516 |
| 40 | 300/300 | 300/300 | 0.621 | 969 |

Takeaway: exact replay of FAISS HNSW is feasible and cheap. Low recall is expected on random high-dimensional data. Not yet covered: inner product/cosine, distance ties, filtered search (`IDSelector`), other FAISS versions. The spike script lived in a session scratchpad that no longer exists; Phase 1 rebuilds it as `ragforensics/replay/` with tests.

## Prior work (checked 2026-10-09)

| Work | What it does | Gap ragforensics fills |
|---|---|---|
| [RAGXRay](https://pypi.org/project/ragxray/) | Heuristic scores for retrieved contexts and answer grounding | Never looks at missing documents |
| [RAGFlip / RAG_Debugger](https://github.com/Elyasirankhah/RAG_Debugger) | Detects queries that break when the retriever changes; proposes repairs with a regression check | Black-box, end-to-end; no per-stage evidence |
| [FaulTrace-RAG](https://github.com/bnssaanirudh/FaulTrace-RAG) | Oracle-replacement counterfactuals + Shapley over retrieval/extraction/aggregation | Coarse stages; not a per-document why-not |
| [RAGChecker](https://arxiv.org/abs/2408.08067) | Claim-level retriever vs generator diagnosis | Doesn't locate the losing retrieval stage |
| [RAGGY](https://arxiv.org/abs/2504.13587) | Interactive RAG debugging UI | No why-not provenance |
| [SmartANN](https://arxiv.org/abs/2609.08240) | Causal diagnosis of ANN index design (aggregate) | Not per query, ANN only |
| [Elasticsearch `_explain`](https://www.elastic.co/guide/en/elasticsearch/reference/8.18/search-explain.html) | Why a document did or didn't match a lexical query | Lexical stage only |
| Ragas / DeepEval / Langfuse | Synthetic test-set generation | Commodity; we reuse the idea, not claim it |
| AutoRAG | Global config search | Not per-miss, no evidence |
| Why-not provenance ([PUG](https://arxiv.org/abs/1808.05752)); He & Lo, why-not top-k (ICDE 2012) | Theory of missing answers and minimal query refinement | Relational, not neural retrieval pipelines |
| Retrievability (Azzopardi 2008; [Wilkie & Azzopardi](https://www.dcs.gla.ac.uk/~wilkiec/papers/cikm2014retrievability_analysis.pdf)) | How retrievable each document is across queries | Basis for our corpus audit |
| [HNSW unreachable points](https://arxiv.org/abs/2407.07871); [Steiner-hardness](https://vldb.org/pvldb/vol17/p4668-wang.pdf) | Graph reachability and query hardness | Basis for our ANN miss classes |

Positioning: why-not provenance for neural retrieval pipelines. The integrated, evidence-backed, per-query tool appears new; most building blocks are not, and the write-up must say so.

## Risks (expected, not yet hit)

When one of these actually causes trouble, log it in `challenges.md` and update its status here.

| Risk | Phase | Plan |
|---|---|---|
| HNSW replay drifts on inner product/cosine, distance ties or a new FAISS version | 1 | Property tests over metrics, ef values and planted ties; FAISS pinned `<1.16`; fall back to FAISS's own distance code if float rounding flips an order. Partly de-risked by E1 |
| hnswlib graph is only reachable through undocumented pickled bytes | 1 | Decode the pickled state; separate replayer held to the same fidelity bar |
| Re-implementing the user's stages drifts from their real code | 1–2 | Re-invoke the user's stage callables with gold injected instead of re-implementing them |
| Evidence text doesn't match parsed text exactly (whitespace, hyphenation, PDF errors) | 1–2 | Exact, then normalized, then fuzzy alignment with confidence; failed alignment counts as parse-stage evidence |
| Chunking blame is counterfactual and re-chunking means re-embedding | 2–3 | Split/dilution classes; re-embed only affected documents with a content-hash cache |
| Embedding mismatch (gold exact rank far down) has no natural "kept set" | 2 | Exact rank, similarity gap to k-th result, lexical overlap, rescue by query rewrite or hybrid weight |
| Filtered ANN (post-filter starvation, graph disconnection) | 2, 6 | Replay the walk with the filter; test higher ef, pre-filter and iterative scan |
| "Smallest repair" has no common unit across knobs | 3 | Explicit cost model (latency, re-embedding, rebuild, broken queries); He & Lo-style minimal refinement |
| Side-effect checks are expensive at corpus scale | 3 | Partial replay, caching, early stopping |
| Planted-bug benchmark is circular | 2, 7 | Blind random-perturbation benchmark plus results on real misses |
| Synthetic questions have more than one valid gold chunk | 4 | Ambiguity filter; report the rejection rate |
| PDF tables flatten badly and hide parse losses | 2 | Parsing as its own stage; swappable parser |
| Cross-encoder scores vary with batching or GPU kernels | 2 | Measure drift; documented tolerance; flag verdicts inside it |
| Most vector DBs hide their HNSW graph | 6 | Tier-1 rank-vs-exact diagnosis everywhere; graph replay only where available |
| Someone ships the same idea first | all | Publish early; differentiate on evidence, fidelity, costed repairs |
| FinanceBench is CC-BY-NC | 2 | Download script only; never commit the data |

## Session log

- **2026-10-10.** Decisions recorded (see decision log). Name checked against PyPI and GitHub. `chroma-hnswlib` verified working on Python 3.11. `CLAUDE.md`, `report.md`, `challenges.md` created; `challenges.md` then changed (at the user's request) from a list of expected risks into a log of problems actually hit, with the risks moved here, and narrowed again to project-relevant technical and research problems only (tooling and session friction removed; "matching FAISS's search loop" added). Phase 0 done: uv project (Python 3.11, numpy 2.4.6, faiss-cpu 1.15.1 pinned `<1.16`, chroma-hnswlib 0.7.6), Apache-2.0 license, module layout, smoke tests (3 passed), `uv build` + `twine check` passed.
- **2026-10-09.** Idea review: prior-art search, feasibility analysis, replay spike E1.
