"""Checks that the scoring math stays valid after the weight-shift experiment."""
import os

import pytest

from src import recommender as r
from src.recommender import load_songs, score_song, recommend_songs, MAX_SCORE

CSV = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")


def make_song(**overrides):
    song = {
        "id": 1, "title": "T", "artist": "A", "genre": "pop", "mood": "happy",
        "energy": 0.8, "tempo_bpm": 120.0, "valence": 0.8,
        "danceability": 0.8, "acousticness": 0.2,
    }
    song.update(overrides)
    return song


POP_FAN = {"favorite_genre": "pop", "favorite_mood": "happy",
           "target_energy": 0.8, "likes_acoustic": False}


def test_weights_are_the_experiment_values():
    # Energy doubled (2.0 -> 4.0), genre halved (2.0 -> 1.0)
    assert r.ENERGY_WEIGHT == 4.0
    assert r.GENRE_WEIGHT == 1.0
    assert MAX_SCORE == pytest.approx(7.0)


def test_perfect_match_scores_exactly_max():
    score, _ = score_song(POP_FAN, make_song())
    assert score == pytest.approx(MAX_SCORE)


def test_total_mismatch_scores_zero():
    song = make_song(genre="metal", mood="angry", energy=0.0, acousticness=0.5)
    user = dict(POP_FAN, target_energy=1.0)
    score, _ = score_song(user, song)
    assert score == pytest.approx(0.0)


def test_energy_points_are_linear_in_the_gap():
    user = dict(POP_FAN, favorite_genre="x", favorite_mood="x")
    s_far, _ = score_song(user, make_song(energy=0.3, acousticness=0.5))   # gap 0.5
    s_near, _ = score_song(user, make_song(energy=0.7, acousticness=0.5))  # gap 0.1
    assert s_far == pytest.approx(r.ENERGY_WEIGHT * 0.5)
    assert s_near == pytest.approx(r.ENERGY_WEIGHT * 0.9)


def test_out_of_range_energy_never_goes_negative():
    user = dict(POP_FAN, favorite_genre="x", favorite_mood="x", target_energy=-1.0)
    score, reasons = score_song(user, make_song(energy=0.9, acousticness=0.5))
    assert score == pytest.approx(0.0)
    assert not any("+-" in reason for reason in reasons)


@pytest.mark.parametrize("target", [0.0, 0.25, 0.5, 0.75, 1.0])
@pytest.mark.parametrize("acoustic", [True, False])
def test_every_catalog_score_is_within_bounds(target, acoustic):
    songs = load_songs(CSV)
    user = {"favorite_genre": "pop", "favorite_mood": "happy",
            "target_energy": target, "likes_acoustic": acoustic}
    for song in songs:
        score, _ = score_song(user, song)
        assert 0.0 <= score <= MAX_SCORE + 1e-9


def test_recommendations_are_sorted_high_to_low():
    songs = load_songs(CSV)
    results = recommend_songs(POP_FAN, songs, k=len(songs))
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)
