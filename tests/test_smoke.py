import faiss
import hnswlib
import numpy as np

import ragforensics


def test_package_imports():
    assert ragforensics.__version__ == "0.1.0"


def test_faiss_hnsw_exposes_graph():
    xb = np.random.default_rng(0).standard_normal((200, 8)).astype("float32")
    index = faiss.IndexHNSWFlat(8, 8)
    index.add(xb)
    neighbors = faiss.vector_to_array(index.hnsw.neighbors)
    offsets = faiss.vector_to_array(index.hnsw.offsets)
    assert len(offsets) == 201
    assert neighbors.max() < 200
    assert 0 <= index.hnsw.entry_point < 200


def test_hnswlib_builds_and_searches():
    xb = np.random.default_rng(0).standard_normal((200, 8)).astype("float32")
    index = hnswlib.Index("l2", 8)
    index.init_index(200)
    index.add_items(xb)
    labels, _ = index.knn_query(xb[:1], k=1)
    assert labels[0, 0] == 0
