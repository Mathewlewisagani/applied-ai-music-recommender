"""
Vector Search and Acoustic Embedding Engine.
Implements zero-dependency vector operations: cosine similarity,
Euclidean distance, and hybrid semantic retrieval across audio feature vectors.
"""

import math
from typing import List, Tuple
from applied_ai_recommender.core.models import Song, UserProfile


def dot_product(v1: List[float], v2: List[float]) -> float:
    return sum(a * b for a, b in zip(v1, v2))


def vector_norm(v: List[float]) -> float:
    return math.sqrt(sum(a * a for a in v))


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Computes cosine similarity between two feature vectors in [-1.0, 1.0].
    Returns 0.0 for zero vectors.
    """
    n1 = vector_norm(v1)
    n2 = vector_norm(v2)
    if n1 == 0.0 or n2 == 0.0:
        return 0.0
    val = dot_product(v1, v2) / (n1 * n2)
    # Clamp to prevent float precision issues
    return max(-1.0, min(1.0, val))


def euclidean_distance(v1: List[float], v2: List[float]) -> float:
    """Computes Euclidean distance between two vectors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


class VectorEngine:
    """
    In-memory vector retrieval engine for fast candidate generation.
    Retrieves songs based on multi-dimensional acoustic similarity.
    """
    def __init__(self, catalog: List[Song]):
        self.catalog = catalog
        self._index = {song.id: song.to_feature_vector() for song in catalog}

    def retrieve_candidates(
        self,
        query_vector: List[float],
        top_n: int = 15,
        genre_filter: str = ""
    ) -> List[Tuple[Song, float]]:
        """
        Retrieves top_n songs closest to the query_vector.
        Optionally allows soft or hard genre filtering.
        """
        scored_candidates = []
        for song in self.catalog:
            song_vec = self._index[song.id]
            sim = cosine_similarity(query_vector, song_vec)
            
            # Boost similarity slightly if genre matches directly
            if genre_filter and song.genre == genre_filter.lower():
                sim = min(1.0, sim + 0.05)
                
            scored_candidates.append((song, sim))

        # Sort descending by similarity
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[:top_n]
