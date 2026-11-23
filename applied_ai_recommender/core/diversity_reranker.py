"""
Maximal Marginal Relevance (MMR) Diversity & Serendipity Re-Ranker.
Mitigates the "energy filter bubble" and artist homogenization by balancing
relevance against redundancy in candidate selection.
"""

from typing import List, Tuple
from applied_ai_recommender.core.models import Song, UserProfile
from applied_ai_recommender.core.vector_engine import cosine_similarity


def compute_intra_song_similarity(s1: Song, s2: Song) -> float:
    """Computes similarity between two songs across genre, artist, and acoustic features."""
    vec_sim = cosine_similarity(s1.to_feature_vector(), s2.to_feature_vector())
    norm_vec_sim = max(0.0, (vec_sim + 1.0) / 2.0)
    
    # Penalize artist repetition heavily
    artist_penalty = 0.4 if s1.artist.lower() == s2.artist.lower() else 0.0
    genre_bonus = 0.2 if s1.genre.lower() == s2.genre.lower() else 0.0
    
    total_redundancy = min(1.0, norm_vec_sim + artist_penalty + genre_bonus)
    return total_redundancy


def mmr_rerank(
    scored_candidates: List[Tuple[Song, float, List[str]]],
    lambda_param: float = 0.7,
    top_k: int = 5,
    max_per_artist: int = 2
) -> List[Tuple[Song, float, List[str], float]]:
    """
    Implements Maximal Marginal Relevance (Carbonell & Goldstein, 1998):
    MMR = Argmax_{d in R \\ S} [ lambda * Sim(d, Query) - (1 - lambda) * Max_{d_s in S} Sim(d, d_s) ]

    Args:
        scored_candidates: List of (Song, relevance_score, reasons)
        lambda_param: Tradeoff between relevance (1.0) and diversity (0.0). Default 0.7.
        top_k: Number of recommendations to produce.
        max_per_artist: Guardrail cap preventing any single artist from monopolizing the list.

    Returns:
        List of (Song, final_mmr_score, reasons, diversity_penalty)
    """
    if not scored_candidates:
        return []

    # Normalize relevance scores to [0.0, 1.0] for fair balancing
    max_score = max(cand[1] for cand in scored_candidates) or 1.0
    
    remaining = scored_candidates.copy()
    selected: List[Tuple[Song, float, List[str], float]] = []
    artist_counts = {}

    while len(selected) < top_k and remaining:
        best_cand = None
        best_mmr_score = -float("inf")
        best_redundancy = 0.0

        for cand in remaining:
            song, rel_score, reasons = cand
            norm_rel = rel_score / max_score

            # Artist constraint guardrail
            current_artist_count = artist_counts.get(song.artist.lower(), 0)
            if current_artist_count >= max_per_artist:
                continue

            if not selected:
                # First element selected purely by top relevance
                mmr_val = norm_rel
                max_sim_to_selected = 0.0
            else:
                # Find maximum similarity to any already-selected song
                max_sim_to_selected = max(
                    compute_intra_song_similarity(song, s[0]) for s in selected
                )
                mmr_val = (lambda_param * norm_rel) - ((1.0 - lambda_param) * max_sim_to_selected)

            if mmr_val > best_mmr_score:
                best_mmr_score = mmr_val
                best_cand = cand
                best_redundancy = max_sim_to_selected

        if best_cand is None:
            # If all remaining hit the artist constraint, relax artist cap to fill top_k
            if remaining:
                best_cand = remaining[0]
                best_redundancy = 0.0
            else:
                break

        song, rel_score, reasons = best_cand
        artist_counts[song.artist.lower()] = artist_counts.get(song.artist.lower(), 0) + 1
        
        # Add diversity annotation
        diversity_annotated_reasons = reasons.copy()
        if len(selected) > 0 and best_redundancy < 0.6:
            diversity_annotated_reasons.append(
                f"Serendipity & Diversity boost: fresh acoustic profile vs preceding selections"
            )

        selected.append((song, rel_score, diversity_annotated_reasons, round(best_redundancy, 3)))
        remaining.remove(best_cand)

    return selected
