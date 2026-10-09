# ragforensics: challenges log

Problems actually hit while building the project, and how each was handled. Newest first. Expected risks that haven't happened yet live in the "Risks" section of `report.md`, not here.

Each entry records what happened, how it showed up, what fixed it, and whether it is resolved.

---

### 2026-10-10. The safety hook slows every first file edit
- **What happened:** a pre-tool hook (GateGuard "Fact-Forcing Gate") blocks the first Bash command and the first write or edit of each file until a list of facts is stated.
- **Impact:** setup took noticeably longer; most new files needed a blocked attempt and a retry.
- **Handling:** stated the facts and retried. The user can exempt paths with `GATEGUARD_EXEMPT_GLOBS` if it becomes a drag.
- **Status:** ongoing, minor.

### 2026-10-10. `CLAUDE.md` was not on disk
- **What happened:** the brief had been loaded as `CLAUDE.md` at session start, but the folder only contained `Idea.md`. The idea review had wrongly said the two files were identical copies.
- **Fix:** created `CLAUDE.md` fresh with the agreed plan, kept `Idea.md` unchanged as the original sketch, and corrected the claim to the user.
- **Status:** resolved.

### 2026-10-10. hnswlib would not install on Windows
- **What happened:** `uv add hnswlib` failed; `hnswlib` 0.8.0 ships no Windows wheels, and building from source needs a C++ compiler (MSVC), which this machine doesn't have.
- **Fix:** switched to `chroma-hnswlib` 0.7.6, which has a prebuilt `cp311-win_amd64` wheel. That wheel only goes up to Python 3.11, so the whole project is pinned to 3.11.
- **Status:** resolved; it constrains the Python version (see the decision log in `report.md`).

### 2026-10-10. `uv init --python 3.11` still ran Python 3.12
- **What happened:** the first `chroma-hnswlib` install failed even though a 3.11 wheel existed. The scratch project created with `uv init --bare --python 3.11` was actually running Python 3.12.5, for which no wheel exists.
- **Fix:** an explicit `uv python pin 3.11` (writes `.python-version`).
- **Status:** resolved.

### 2026-10-10. The replay spike script was lost
- **What happened:** the session scratchpad holding `replay_spike.py` was removed mid-session.
- **Impact:** the code is gone; its results are recorded in `report.md` (E1).
- **Fix:** Phase 1 rebuilds it properly as `src/ragforensics/replay/` with tests.
- **Status:** resolved by plan.

### 2026-10-09. Integer types in FAISS graph arrays crashed the replay
- **What happened:** the first spike run failed with `TypeError: slice indices must be integers`. `hnsw.offsets` comes back as unsigned 64-bit and `cum_nneighbor_per_level` as 32-bit integers; numpy turns their sum into a float.
- **Fix:** convert both to plain Python `int` before slicing.
- **Status:** resolved; the Phase 1 replayer must do the same.

### 2026-10-09. Prior-art claims in the brief that could not be verified
- **What happened:** the brief cites "Ferryte (PyPI)"; it could not be found on PyPI or the web. A search snippet described a close competitor, `rag-regression-debugger`, but its GitHub repo returned 404.
- **Handling:** Ferryte left out of the prior-work table; `rag-regression-debugger` noted only as a scoop-risk signal.
- **Status:** resolved (documented).
