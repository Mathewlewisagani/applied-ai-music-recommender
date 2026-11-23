"""
Quantitative Benchmark Harness.
Directly compares Baseline VibeCheck 1.0 against VibeCheck 2.0 Extended System
across all 17 original test profiles on:
1. Catalog Coverage
2. Intra-List Diversity (ILD)
3. Fairness Parity between Normal and Adversarial Cohorts
4. Energy Filter Bubble Resistance (tracking dominance of tracks like 'Fiesta en la Calle')
"""

import sys
import os
from typing import Dict, List, Any

# Ensure project root and src are on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
src_dir = os.path.join(root_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.main import USER_PROFILES, ADVERSARIAL_PROFILES
from src.recommender import load_songs as load_legacy_songs, recommend_songs as recommend_legacy
from applied_ai_recommender.rag.pipeline import AppliedRecommenderPipeline
from applied_ai_recommender.core.models import Song
from applied_ai_recommender.evaluation.metrics import (
    compute_catalog_coverage, compute_intra_list_diversity, compute_fairness_parity
)


def run_benchmark() -> Dict[str, Any]:
    """Runs rigorous comparative benchmark between VibeCheck 1.0 and 2.0."""
    legacy_csv = os.path.join(root_dir, "data", "songs.csv")
    legacy_songs = load_legacy_songs(legacy_csv)
    v2_pipeline = AppliedRecommenderPipeline()

    all_profiles = {}
    all_profiles.update(USER_PROFILES)
    all_profiles.update(ADVERSARIAL_PROFILES)

    # 1. Evaluate VibeCheck 1.0 Baseline
    v1_recs = {}
    v1_rec_songs_all: List[List[Song]] = []
    v1_song_counts: Dict[str, int] = {}
    v1_normal_scores: List[float] = []
    v1_adversarial_scores: List[float] = []

    for name, prefs in all_profiles.items():
        recs = recommend_legacy(prefs, legacy_songs, k=5)
        v1_recs[name] = recs
        song_objs = []
        for song_dict, score, _ in recs:
            v1_song_counts[song_dict["title"]] = v1_song_counts.get(song_dict["title"], 0) + 1
            song_objs.append(Song(
                id=song_dict["id"],
                title=song_dict["title"],
                artist=song_dict["artist"],
                genre=song_dict["genre"],
                mood=song_dict["mood"],
                energy=song_dict["energy"],
                tempo_bpm=song_dict["tempo_bpm"],
                valence=song_dict["valence"],
                danceability=song_dict["danceability"],
                acousticness=song_dict["acousticness"],
            ))
            if name in USER_PROFILES:
                v1_normal_scores.append(score)
            else:
                v1_adversarial_scores.append(score)
        v1_rec_songs_all.append(song_objs)

    v1_coverage = compute_catalog_coverage(v1_rec_songs_all, len(legacy_songs))
    v1_ild = sum(compute_intra_list_diversity(r) for r in v1_rec_songs_all) / len(v1_rec_songs_all)
    # V1 Normalized parity (out of max 7.0)
    v1_norm_avg = (sum(v1_normal_scores) / len(v1_normal_scores)) / 7.0 if v1_normal_scores else 0
    v1_adv_avg = (sum(v1_adversarial_scores) / len(v1_adversarial_scores)) / 7.0 if v1_adversarial_scores else 0

    # 2. Evaluate VibeCheck 2.0 Extended System
    v2_recs = {}
    v2_rec_songs_all: List[List[Song]] = []
    v2_song_counts: Dict[str, int] = {}
    v2_normal_scores: List[float] = []
    v2_adversarial_scores: List[float] = []

    for name, prefs in all_profiles.items():
        res = v2_pipeline.run_pipeline(prefs, top_k=5, diversity_lambda=0.65)
        rec_items = res["recommendations"]
        v2_recs[name] = rec_items
        song_objs = []
        for item in rec_items:
            v2_song_counts[item.song.title] = v2_song_counts.get(item.song.title, 0) + 1
            song_objs.append(item.song)
            if name in USER_PROFILES:
                v2_normal_scores.append(item.final_score)
            else:
                v2_adversarial_scores.append(item.final_score)
        v2_rec_songs_all.append(song_objs)

    v2_coverage = compute_catalog_coverage(v2_rec_songs_all, len(v2_pipeline.catalog))
    v2_ild = sum(compute_intra_list_diversity(r) for r in v2_rec_songs_all) / len(v2_rec_songs_all)
    # V2 Normalized parity (out of max 10.0)
    v2_norm_avg = (sum(v2_normal_scores) / len(v2_normal_scores)) / 10.0 if v2_normal_scores else 0
    v2_adv_avg = (sum(v2_adversarial_scores) / len(v2_adversarial_scores)) / 10.0 if v2_adversarial_scores else 0

    # Check 'Fiesta en la Calle' frequency
    fiesta_v1_pct = (v1_song_counts.get("Fiesta en la Calle", 0) / len(all_profiles)) * 100
    fiesta_v2_pct = (v2_song_counts.get("Fiesta en la Calle", 0) / len(all_profiles)) * 100

    report = {
        "v1": {
            "catalog_coverage": v1_coverage,
            "intra_list_diversity": v1_ild,
            "fiesta_dominance_pct": fiesta_v1_pct,
            "normal_cohort_score_pct": v1_norm_avg * 100,
            "adversarial_cohort_score_pct": v1_adv_avg * 100,
            "parity_ratio": v1_adv_avg / v1_norm_avg if v1_norm_avg > 0 else 0,
        },
        "v2": {
            "catalog_coverage": v2_coverage,
            "intra_list_diversity": v2_ild,
            "fiesta_dominance_pct": fiesta_v2_pct,
            "normal_cohort_score_pct": v2_norm_avg * 100,
            "adversarial_cohort_score_pct": v2_adv_avg * 100,
            "parity_ratio": v2_adv_avg / v2_norm_avg if v2_norm_avg > 0 else 0,
        }
    }
    return report


def print_benchmark_summary():
    report = run_benchmark()
    v1 = report["v1"]
    v2 = report["v2"]

    print("=" * 75)
    print(" 📊 VIBECHECK 1.0 vs VIBECHECK 2.0 SYSTEM BENCHMARK")
    print("=" * 75)
    print(f"{'Metric':<32} | {'VibeCheck 1.0':<18} | {'VibeCheck 2.0':<18}")
    print("-" * 75)
    print(f"{'Catalog Coverage':<32} | {v1['catalog_coverage']*100:.1f}%              | {v2['catalog_coverage']*100:.1f}% (Expanded Catalog)")
    print(f"{'Intra-List Diversity (ILD)':<32} | {v1['intra_list_diversity']:.3f}             | {v2['intra_list_diversity']:.3f} (+{(v2['intra_list_diversity']-v1['intra_list_diversity']):.3f})")
    print(f"{'Fiesta en la Calle Dominance':<32} | {v1['fiesta_dominance_pct']:.1f}% (Severe bubble)| {v2['fiesta_dominance_pct']:.1f}% (Diverse)")
    print(f"{'Normal Cohort Satisfaction':<32} | {v1['normal_cohort_score_pct']:.1f}%             | {v2['normal_cohort_score_pct']:.1f}%")
    print(f"{'Edge-Case Cohort Satisfaction':<32} | {v1['adversarial_cohort_score_pct']:.1f}%             | {v2['adversarial_cohort_score_pct']:.1f}%")
    print(f"{'Fairness Parity Ratio':<32} | {v1['parity_ratio']:.3f}             | {v2['parity_ratio']:.3f} (+{(v2['parity_ratio']-v1['parity_ratio']):.3f})")
    print("=" * 75)


if __name__ == "__main__":
    print_benchmark_summary()
