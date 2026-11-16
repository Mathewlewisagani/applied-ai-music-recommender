# 🎵 Music Recommender Simulation

## Project Summary

**VibeCheck 1.0** is a small content-based music recommender that runs in the terminal. It reads a catalog of 20 songs from `data/songs.csv`. It scores each song against a listener's taste profile: favorite genre, favorite mood, target energy, and whether they like acoustic music. Then it prints the top 5 songs, each with a score and a list of reasons.

`src/main.py` runs 17 test listeners. 10 are "normal" listeners built around one genre each. 7 are edge-case listeners designed to trick the scoring, such as conflicting preferences, misspelled genres, and out-of-range energy. I also ran a weight-shift experiment (genre halved, energy doubled) and documented where the system works, where it's biased, and why, in the [model card](model_card.md).

---

## How The System Works

Real-world recommenders rank songs using two main approaches: what similar users like (collaborative filtering) and what the song itself is like (content-based filtering). This system is content-based. It compares each song's features to one user's stated preferences.

**Song features**

Each `Song` has: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, and acousticness.

The score uses only four of them: **genre, mood, energy, and acousticness**. The others are left out because they mostly repeat information already captured:

- danceability and tempo_bpm rise and fall with energy
- valence closely follows mood (happy songs have high valence)
- id, title, and artist are metadata that identify a song but don't describe how it sounds

**User profile**

Each `UserProfile` stores:

- `favorite_genre` (e.g. "lofi")
- `favorite_mood` (e.g. "chill")
- `target_energy`, a number from 0 to 1
- `likes_acoustic`, true or false

**Scoring rule (one song → one number)**

Each song starts at 0 and earns points:

| Check | Points (current) | Original |
|---|---|---|
| Genre matches `favorite_genre` | +1.0 | +2.0 |
| Mood matches `favorite_mood` | +1.0 | +1.0 |
| Energy closeness: `4.0 × max(0, 1 - abs(song.energy - target_energy))` | 0 to +4.0 | 0 to +2.0 |
| Acoustic match: `likes_acoustic` and acousticness > 0.6, or not `likes_acoustic` and acousticness < 0.4 | +1.0 | +1.0 |
| **Maximum score** | **7.0** | 6.0 |

The current weights come from the weight-shift experiment (see [Experiments You Tried](#experiments-you-tried)). They are named constants at the top of `src/recommender.py`, so you can go back to the original weights by changing `GENRE_WEIGHT` and `ENERGY_WEIGHT`. In the original design, genre had the most weight because it seemed like the strongest sign of taste. Energy is scored by how close it is to the target, not by how high it is, so a user who wants calm music is not pushed toward loud songs. Each check that adds points also records a short reason (e.g. "genre match +2.0"), which is used to explain the recommendation.

**Ranking rule (all scores → top k list)**

1. Score every song in the catalog.
2. Sort the songs from highest to lowest score.
3. If two songs tie, order them by title so the results are the same on every run.
4. Return the top `k` songs (default 5) with their scores and reasons.

**Data flow**

```
songs.csv ──load_songs()──► list of songs ─┐
                                           ├─► score every song ─► sort high → low ─► top 5 + reasons
USER_PROFILES ──pick one user──────────────┘
```

`main.py` repeats this for every user in `USER_PROFILES`.

**Expected biases and limitations**

- **Genre may be over-prioritized.** A genre match is worth +2.0, the same as a perfect energy match. A song in the wrong genre that fits the user's mood, energy, and acoustic taste can still lose to a weaker song in the right genre.
- **Exact text matching misses similar labels.** "pop" does not match "indie pop", and "sad" does not match "melancholic", so closely related songs get no credit.
- **Uneven catalog.** Lofi has 3 songs while most genres have only 1. Lofi fans get several genre matches; a metal or folk fan gets one, and the rest of their list is filled by energy alone, often with songs from unrelated genres.
- **Acoustic gap.** Songs with acousticness between 0.4 and 0.6 never earn the acoustic point, whatever the user prefers.
- **No learning or variety.** The profile is fixed, the system ignores listening history, and nothing stops the top 5 from being very similar songs.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app from the `src` folder (it loads `../data/songs.csv` by relative path):

   ```bash
   cd src
   python main.py
   ```

### Running Tests

From the project root, run:

```bash
pytest
```

- `tests/test_recommender.py`: starter tests for the `Recommender` class (ranking and explanations).
- `tests/test_scoring.py`: checks the scoring math. A perfect match scores exactly the max, a total miss scores 0, energy points scale evenly with the gap, out-of-range energy never goes negative, and every catalog song stays within 0 and the max.

All 18 tests pass.

---

## Sample Recommendation Output

Terminal output for the default "Happy Pop Fan" profile (pop, happy, energy 0.8, not acoustic), run from the `src` folder with `python main.py`:

```
Loading songs from ../data/songs.csv...
Loaded 20 songs.

============================================================
 Happy Pop Fan
 genre: pop | mood: happy | energy: 0.80 | acoustic: no
============================================================

 1. Sunrise City (Neon Echo)
    Score: 6.92 / 7.00
    Reasons:
      - genre match: pop (+1.0)
      - mood match: happy (+1.0)
      - energy 0.82 vs target 0.80 (+3.92)
      - non-acoustic sound: 0.18 (+1.0)

 2. Rooftop Lights (Indigo Parade)
    Score: 5.84 / 7.00
    Reasons:
      - mood match: happy (+1.0)
      - energy 0.76 vs target 0.80 (+3.84)
      - non-acoustic sound: 0.35 (+1.0)

 3. Gym Hero (Max Pulse)
    Score: 5.48 / 7.00
    Reasons:
      - genre match: pop (+1.0)
      - energy 0.93 vs target 0.80 (+3.48)
      - non-acoustic sound: 0.05 (+1.0)

 4. Concrete Crown (Block Theory)
    Score: 4.92 / 7.00
    Reasons:
      - energy 0.78 vs target 0.80 (+3.92)
      - non-acoustic sound: 0.12 (+1.0)

 5. Fiesta en la Calle (Los Brillantes)
    Score: 4.84 / 7.00
    Reasons:
      - energy 0.84 vs target 0.80 (+3.84)
      - non-acoustic sound: 0.38 (+1.0)
```

Sunrise City matches all four checks and scores almost the maximum. Rooftop Lights is "indie pop", so it gets no genre credit, but its happy mood and close energy put it 2nd. Gym Hero is pop but loses the mood point because it's "intense." With the original weights (genre +2.0), Gym Hero ranked 2nd, ahead of Rooftop Lights. Places 4 and 5 match only on energy and sound, not genre or mood.

---

## Experiments You Tried

**1. Weight shift: genre halved (2.0 → 1.0), energy doubled (2.0 → 4.0).**

- In 12 of 17 profiles, the top 5 stayed exactly the same. Only the scores went up.
- **Happy Pop Fan:** Rooftop Lights (happy) moved above Gym Hero (intense). This is better.
- **Perfectly Average** (blues, happy): a happy song took #1 from the only blues song, which is melancholic. This is better too.
- **Unplugged Metalhead:** calm acoustic filler was replaced by loud electronic songs. Closer in energy, but further from "acoustic."
- **Verdict:** mostly *different*, only slightly more accurate. The change also made energy dominate even more. It's now 4 of the 7 points, so mood matters even less.

**2. Edge-case ("adversarial") profiles.** I built 7 listeners designed to trick the scoring:

| Profile | What happened |
|---|---|
| Sad but Hyped (sad mood, 0.9 energy) | Never got the catalog's one sad song. Energy beat mood. |
| Ghost Genre (k-pop, dreamy) | No warning. Still got a confident-looking top 5. |
| Caps Lock Pop Fan ("Pop", "Happy") | Matching is case-sensitive, so it lost every genre and mood point. |
| Below Zero Energy (−1.0) | Gave negative scores under the original code. Now clamped to 0. |
| Unplugged Metalhead (acoustic metal) | The metal song still won. The rest of the list was mixed filler. |
| Perfectly Average (blues, happy) | Under the original weights, genre beat an opposite mood. |
| Conflicted Listener (metal, peaceful) | Got the exact same list as the Classical Listener. Its genre was ignored. |

**3. Different types of users.** Listeners with clear, consistent tastes (Chill Studier, Gym Goer) got great lists. Their #1 was always right, and opposite listeners shared no songs. Listeners with only one song in their genre got a good #1 and then filler picked mostly by energy. Full terminal output and side-by-side comparisons are in the [model card](model_card.md#7-evaluation).

---

## Limitations and Risks

- **Tiny, uneven catalog.** Only 20 made-up songs. Most genres have just 1 song, so after the #1 pick, the list is filled by songs with similar energy from unrelated genres.
- **Energy filter bubble.** Energy is worth 4 of the 7 points, so mood barely counts. The same upbeat songs keep showing up. *Fiesta en la Calle* is in the top 5 for 9 of the 17 profiles.
- **Mood and energy are tied together in the data.** Every sad song is quiet, so a "sad but energetic" listener can't be served.
- **Exact text matching.** "Pop" ≠ "pop", "indie pop" ≠ "pop", and "sad" ≠ "melancholic." Typos and near-matches get no credit, and unknown genres don't trigger a warning.
- **Acoustic dead zone.** Songs with acousticness between 0.4 and 0.6 never earn the sound point.
- **No learning, no context.** The profile is fixed. The system doesn't understand lyrics, language, or listening history, and it doesn't add variety to the top 5.

More detail is in the [model card](model_card.md#6-limitations-and-bias).

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

This project showed me how a recommender turns data into a prediction. Each song becomes a few numbers and labels. The user's taste becomes a matching set of preferences. A scoring rule turns "how well do these match?" into one number, and sorting those numbers gives the recommendation. Even a rule this simple, just adding up points from four checks, produces lists that *feel* like real recommendations, especially when each pick explains its reasons. I also learned the two main approaches: collaborative filtering (what similar users like) and content-based filtering (what the song itself is like). Mine is content-based.

Bias shows up in places that are easy to miss. The weights decide whose preferences count. When energy is worth more than mood, a listener whose mood and energy don't usually go together gets ignored. The data adds its own bias. Most genres have one song and the middle energy range is nearly empty, so some listeners get thoughtful lists while others get filler, and the same few songs keep showing up for everyone. Exact text matching quietly penalizes anyone who types a label differently. None of these are obvious from looking at the code. They only showed up when I tested unusual users, which is why testing edge cases matters for real recommenders too.



