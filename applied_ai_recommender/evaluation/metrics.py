"""
Evaluation Metrics for Applied AI Recommender Systems.
Computes evaluation metrics beyond accuracy:
- Catalog Coverage
- Intra-List Diversity (ILD)
- Novelty / Serendipity
- Cohort Fairness & Parity Disparity
"""

import math
from typing import List, Dict, Set, Any
from applied_ai_recommender.core.models import Song, RecommendationItem
from applied_ai_recommender.core.vector_engine import euclidean_distance


def compute_catalog_coverage(all_recommendations: List[List[Song]], total_catalog_size: int) -> float:
    """
    Computes the proportion of unique catalog items recommended across all users.
    Coverage = |Union(Recs)| / |Catalog|
    """
    if total_catalog_size == 0:
        return 0.0
    unique_ids: Set[int] = set()
    for rec_list in all_recommendations:
        for song in rec_list:
            unique_ids.add(song.id)
    return len(unique_ids) / float(total_catalog_size)


def compute_intra_list_diversity(recommendations: List[Song]) -> float:
    """
    Computes average pairwise acoustic distance between songs in a recommendation list.
    Higher values indicate greater variety; low values indicate a repetitive filter bubble.
    """
    k = len(recommendations)
    if k <= 1:
        return 0.0

    total_dist = 0.0
    pairs = 0
    for i in range(k):
        for j in range(i + 1, k):
            dist = euclidean_distance(
                recommendations[i].to_feature_vector(),
                recommendations[j].to_feature_vector()
            )
            total_dist += dist
            pairs += 1

    return total_dist / pairs if pairs > 0 else 0.0


def compute_novelty(recommendations: List[Song], item_popularity: Dict[int, int], total_users: int) -> float:
    """
    Computes Shannon-information based Novelty:
    Novelty = -1/K * sum(log2(p(i)))
    Higher values mean the system recommends rare/long-tail tracks rather than just hits.
    """
    if not recommendations or total_users == 0:
        return 0.0

    scores = []
    for song in recommendations:
        count = item_popularity.get(song.id, 1)
        prob = count / float(total_users)
        scores.append(-math.log2(max(0.001, prob)))

    return sum(scores) / len(scores)


def compute_fairness_parity(cohort_scores: Dict[str, List[float]]) -> Dict[str, float]:
    """
    Calculates fairness metrics across demographic/persona cohorts:
    - mean score per cohort
    - disparity gap (max cohort score - min cohort score)
    - parity ratio (min cohort score / max cohort score)
    """
    averages = {cohort: (sum(scores) / len(scores) if scores else 0.0)
                for cohort, scores in cohort_scores.items()}

    if not averages:
        return {"disparity_gap": 0.0, "parity_ratio": 1.0}

    max_val = max(averages.values())
    min_val = min(averages.values())
    disparity_gap = max_val - min_val
    parity_ratio = (min_val / max_val) if max_val > 0 else 1.0

    return {
        "cohort_averages": averages,
        "disparity_gap": round(disparity_gap, 3),
        "parity_ratio": round(parity_ratio, 3),
    }
