"""
Embed every distinct cleaned tag with all-mpnet-base-v2, the student's choice of model.

    uv run python embed_tags.py

Writes `tag_embeddings_0.npz` and `tag_embeddings_1.npz`: every tag after `clean_tag()`, the
student's rule (stripped and lowercased, the judge's rule), and one unit-length vector each, so cosine similarity is
a dot product. Two files because one is over GitHub's 100 MB limit. Run once;
part2_tags.py reads them through `load_embeddings()` and never loads the model.
"""

from pathlib import Path

import numpy as np
from load_data import load_tags

HERE = Path(__file__).parent
SHARDS = [HERE / f"tag_embeddings_{i}.npz" for i in range(2)]


def clean_tag(tags):
    """The student's merge rule, the same one the judge uses: strip, then lowercase."""
    return tags.str.strip().str.lower()


def load_embeddings():
    """tag string -> row number, and the matrix of unit vectors in that row order."""
    parts = [np.load(path, allow_pickle=True) for path in SHARDS]
    tags = np.concatenate([p["tags"] for p in parts])
    vectors = np.concatenate([p["vectors"] for p in parts])
    return {t: i for i, t in enumerate(tags)}, vectors


if __name__ == "__main__":
    # imported here so that load_embeddings() never needs the model or torch
    from sentence_transformers import SentenceTransformer

    strings = sorted(clean_tag(load_tags()["tag"]).unique())
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    vectors = model.encode(strings, batch_size=256, show_progress_bar=True,
                           normalize_embeddings=True)
    tags = np.array(strings, dtype=object)
    for path, rows in zip(SHARDS, np.array_split(np.arange(len(tags)), len(SHARDS))):
        np.savez_compressed(path, tags=tags[rows], vectors=vectors[rows].astype(np.float16))
    print(f"{len(strings):,} cleaned tags embedded, {vectors.shape[1]} dimensions, "
          f"written to {', '.join(p.name for p in SHARDS)}")
