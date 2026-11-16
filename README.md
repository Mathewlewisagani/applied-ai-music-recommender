# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

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

| Check | Points |
|---|---|
| Genre matches `favorite_genre` | +2.0 |
| Mood matches `favorite_mood` | +1.0 |
| Energy closeness: `2.0 × (1 - abs(song.energy - target_energy))` | 0 to +2.0 |
| Acoustic match: `likes_acoustic` and acousticness > 0.6, or not `likes_acoustic` and acousticness < 0.4 | +1.0 |

> **Experiment update:** in the weight-shift experiment, genre was cut to +1.0 and energy raised to 0–4.0 (max score 7.0). See the Evaluation section of [model_card.md](model_card.md). The table above shows the original weights.

With the original weights the highest possible score is 6.0. Genre has the most weight because it is the strongest sign of taste. Energy is scored by how close it is to the target, not by how high it is, so a user who wants calm music is not pushed toward loud songs. Each check that adds points also records a short reason (e.g. "genre match +2.0"), which is used to explain the recommendation.

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

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

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
    Score: 5.96 / 6.00
    Reasons:
      - genre match: pop (+2.0)
      - mood match: happy (+1.0)
      - energy 0.82 vs target 0.80 (+1.96)
      - non-acoustic sound: 0.18 (+1.0)

 2. Gym Hero (Max Pulse)
    Score: 4.74 / 6.00
    Reasons:
      - genre match: pop (+2.0)
      - energy 0.93 vs target 0.80 (+1.74)
      - non-acoustic sound: 0.05 (+1.0)

 3. Rooftop Lights (Indigo Parade)
    Score: 3.92 / 6.00
    Reasons:
      - mood match: happy (+1.0)
      - energy 0.76 vs target 0.80 (+1.92)
      - non-acoustic sound: 0.35 (+1.0)

 4. Concrete Crown (Block Theory)
    Score: 2.96 / 6.00
    Reasons:
      - energy 0.78 vs target 0.80 (+1.96)
      - non-acoustic sound: 0.12 (+1.0)

 5. Fiesta en la Calle (Los Brillantes)
    Score: 2.92 / 6.00
    Reasons:
      - energy 0.84 vs target 0.80 (+1.92)
      - non-acoustic sound: 0.38 (+1.0)
```

Sunrise City matches all four checks and scores almost the maximum. Gym Hero is still pop but loses the mood point (it is "intense"). Rooftop Lights is "indie pop", so it gets no genre credit even though it is close to pop. Places 4 and 5 match only on energy and sound, not genre or mood.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



