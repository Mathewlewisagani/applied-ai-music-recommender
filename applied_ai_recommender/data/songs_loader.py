"""
Data loading and ingestion pipeline.
Supports both legacy VibeCheck 1.0 CSV format (10 columns)
and enriched VibeCheck 2.0 format (15 columns).
"""

import csv
import os
from typing import List, Optional
from applied_ai_recommender.core.models import Song


def load_catalog(csv_path: Optional[str] = None) -> List[Song]:
    """
    Loads catalog from specified CSV path or defaults to enriched_songs.csv.
    Gracefully handles missing columns by populating defaults.
    """
    if csv_path is None:
        base_dir = os.path.dirname(__file__)
        csv_path = os.path.join(base_dir, "enriched_songs.csv")

    if not os.path.exists(csv_path):
        # Fallback to starter data if not found
        fallback = os.path.join(os.path.dirname(__file__), "..", "..", "data", "songs.csv")
        if os.path.exists(fallback):
            csv_path = fallback
        else:
            raise FileNotFoundError(f"Cannot find catalog file at {csv_path}")

    songs: List[Song] = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = Song(
                id=int(row["id"]),
                title=row["title"].strip(),
                artist=row["artist"].strip(),
                genre=row["genre"].strip().lower(),
                mood=row["mood"].strip().lower(),
                energy=float(row["energy"]),
                tempo_bpm=float(row["tempo_bpm"]),
                valence=float(row["valence"]),
                danceability=float(row["danceability"]),
                acousticness=float(row["acousticness"]),
                instrumentalness=float(row.get("instrumentalness", 0.0)),
                speechiness=float(row.get("speechiness", 0.0)),
                key_instruments=row.get("key_instruments", "").strip(),
                listening_context=row.get("listening_context", "").strip(),
                vibe_description=row.get("vibe_description", "").strip(),
            )
            songs.append(song)

    return songs
