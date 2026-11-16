# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeCheck 1.0**

It checks how well each song matches your vibe: your genre, mood, energy, and sound.

---

## 2. Goal and Intended Use  

**Goal / task.** VibeCheck suggests songs. You tell it what you like, and it gives you the 5 songs from its catalog that fit best. Each pick comes with a short list of reasons.

**What it assumes about you.**

- You have one favorite genre and one favorite mood.
- You know roughly how much energy you want, on a scale from 0 (calm) to 1 (intense).
- You either like acoustic music or you don't.
- Your taste doesn't change. It doesn't learn from what you play or skip.

**Intended use.**

- A classroom project for learning how recommenders turn data into rankings.
- Trying out different "listeners" and seeing how the scoring reacts.
- Finding where simple scoring rules break or show bias.

**Not intended for.**

- Real users or a real music app. The catalog is only 20 made-up songs.
- Judging what music is "good." It only measures how well a song matches a few labels.
- Making decisions about people, like guessing someone's mood or personality from their music.
- Listeners whose taste doesn't fit one genre and one mood. It can't handle mixed or changing tastes.

---

## 3. How the Model Works  

This is a content-based recommender. It doesn't look at what other people listen to. It compares the details of each song to what one user says they like.

**What it looks at in each song.** Every song in the catalog has a genre (like pop or folk), a mood (like happy or sad), an energy level from 0 (very calm) to 1 (very intense), and an acousticness level from 0 (electronic or heavily produced) to 1 (acoustic instruments). The catalog also lists tempo, danceability, and valence (how positive a song sounds), but the model ignores them. Tempo and danceability mostly go up and down with energy, and valence mostly follows mood, so counting them would score the same thing twice.

**What it knows about the user.** Each user has four preferences: a favorite genre, a favorite mood, how much energy they want, and whether they like acoustic music.

**How a song gets its score.** Every song starts at 0 and earns points, up to a maximum of 7. These are the current weights from the weight-shift experiment (see Evaluation). The original weights are shown in brackets.

- **1 point** if the genre is the user's favorite *(was 2 points)*.
- **1 point** if the mood is the user's favorite.
- **Up to 4 points** for energy, based on how close the song is to the user's target *(was up to 2)*. A perfect match gets all 4 points, and the further away the song is, the fewer points it gets. Points never drop below 0, even if the target is outside the 0 to 1 range. Closeness counts, not loudness, so someone who wants calm music isn't pushed toward loud songs.
- **1 point** if the sound fits: a clearly acoustic song for a user who likes acoustic music, or a clearly non-acoustic song for a user who doesn't.

The weights are named constants at the top of `src/recommender.py` (`GENRE_WEIGHT`, `ENERGY_WEIGHT`, and so on), so the original setup can be restored by changing two numbers.

Every time a song earns points, the model writes down why (for example, "genre match: pop"), so each recommendation comes with its reasons.

**How it picks the final list.** After every song is scored, the model sorts them from highest to lowest score and shows the top 5. If two songs tie, they are listed alphabetically by title so the results are the same every time.

**Changes from the starter.** The starter code returned the first few songs in the file without scoring them. This version loads the full catalog (expanded from 10 to 20 songs with 10 new genres and moods), scores every song with the rules above, ranks them, and explains each pick.

---

## 4. Data  

**Size.** 20 songs in `data/songs.csv`. The starter had 10. I added 10 more to cover more genres and moods.

**Features for each song.** Title, artist, genre, mood, energy, tempo, valence (how positive it sounds), danceability, and acousticness. The model only uses 4 of these: **genre, mood, energy, and acousticness.**

**What's in it.**

- 17 genres, including pop, lofi, rock, metal, jazz, classical, hip hop, country, EDM, folk, blues, reggae, latin, and R&B.
- 16 moods, including happy, chill, intense, sad, angry, romantic, and nostalgic.

**Limits.**

- It's tiny. A real app has millions of songs.
- Most genres have only **1 song**. Lofi has 3 and pop has 2.
- Energy is lopsided. 9 songs are high-energy, 8 are low-energy, and only 3 are in the middle.
- Mood and energy are tied together. Every sad song is quiet, and every loud song is upbeat or angry. There's no "sad but energetic" song.
- The songs and numbers are made up. They don't come from real listening data.
- Each song has just one genre and one mood. Real songs often mix styles.
- No lyrics, language, era, or artist popularity.

---

## 5. Strengths  

- **The #1 pick is almost always right.** All 10 "normal" listeners got a song from their favorite genre at #1, usually with a near-perfect score.
- **Clear tastes work best.** Listeners whose genre, mood, and energy all agree get great results. Examples: Chill Studier (soft lofi) and Gym Goer (loud EDM).
- **Calm stays calm, loud stays loud.** Energy is scored by closeness, not by how high it is. So a calm listener never gets pushed toward heavy songs.
- **Opposites really are opposite.** Chill Studier and Gym Goer have zero songs in common, which matches intuition.
- **Every pick explains itself.** Each song shows exactly which checks it passed and how many points each gave. That makes it easy to see why a song showed up.
- **Same input, same output.** Ties are broken by title, so results never change between runs.

---

## 6. Limitations and Bias 

**Main weakness: an energy "filter bubble" that ignores mood.** After the weight shift, energy is worth 4 of the 7 points, so the system mostly sorts songs by how calm or intense they are, and mood (1 point) barely matters. A listener whose mood and energy don't usually go together gets their mood ignored. The "Sad but Hyped" user never sees the catalog's only sad song, because every sad-sounding song in the catalog is also quiet. The catalog makes this worse: 9 of the 20 songs have energy above 0.7 and 8 are below 0.45, but only 3 sit in the middle, so high-energy users keep getting the same handful of upbeat songs. *Fiesta en la Calle* shows up in the top 5 for 9 of the 17 profiles. The result is a filter bubble where "energetic" quietly turns into "happy party music" and "sad" into "quiet acoustic music," and users who don't fit those pairings are poorly served.

**Other weaknesses found while testing**

- **Exact text matching.** "Pop" ≠ "pop", "indie pop" ≠ "pop", and "sad" ≠ "melancholic", so near-matches and typos get no credit.
- **Uneven genres.** Lofi has 3 songs and most genres have 1, so a lofi fan gets several genre matches while a metal or folk fan gets one and then filler.
- **Acoustic dead zone.** Songs with acousticness between 0.4 and 0.6 never earn the sound point, whatever the user prefers.
- **No warnings.** Unknown genres or moods still produce a confident-looking top 5.

---

## 7. Evaluation  

**In short:**

- I tested 17 listener profiles: 10 normal ones and 7 "trick" ones built to confuse the scoring.
- I compared pairs of profiles to check that different tastes gave sensibly different results.
- I ran one experiment: genre weight cut in half, energy weight doubled.
- I wrote automated tests to make sure scores always stay between 0 and 7. All 18 pass.
- The details are below.

### Profiles I tested

I tested **17 listener profiles** in `src/main.py`:

- **10 "normal" listeners**, each built around one genre: Happy Pop Fan, Chill Studier (lofi), Gym Goer (EDM), Headbanger (metal), Classical Listener, Sad Folk Fan, Late Night R&B, Hip Hop Head, Country Roads, and Party Starter (latin).
- **7 "trick" listeners** built to confuse the scoring: Conflicted Listener, Sad but Hyped, Ghost Genre, Caps Lock Pop Fan, Below Zero Energy, Unplugged Metalhead, and Perfectly Average.

For each one I checked: does the #1 song actually fit what this person asked for, and do songs 2 to 5 make sense, or are they random filler?

I also added automated tests (`tests/test_scoring.py`) that check the math: a perfect song scores exactly 7, a total miss scores exactly 0, energy points shrink evenly as the gap grows, and no song in the catalog ever scores below 0 or above 7. All 18 tests pass.

### What surprised me

- **#1 was almost always right, but #2 to #5 often weren't.** Every normal listener got their genre's song at #1. But most genres have only one song, so the rest of the list is filled by whatever has a similar energy level, even if it's a completely different style.
- **The same few songs show up for everybody.** *Fiesta en la Calle*, *Sunrise City*, *Gym Hero*, and *Concrete Crown* each landed in the top 5 for 6 to 9 different profiles, because they sit in the crowded high-energy part of the catalog.
- **Typing "Pop" instead of "pop" wipes out most of the score.** The computer treats them as different words.
- **Mood barely matters.** A user who asked for "sad" never got the sad song unless they also asked for low energy.

### Why does "Gym Hero" keep showing up for the Happy Pop Fan?

Imagine the recommender as a judge with a checklist: *right genre? right mood? right energy? right sound?* *Gym Hero* is labeled **pop**, it is **high-energy** (0.93, close to the fan's 0.8), and it is **electronic, not acoustic**. That's 3 out of 4 boxes ticked. The only box it misses is mood: it is tagged "intense" rather than "happy." The judge doesn't know that a pounding workout track *feels* different from a sunny pop song. It only sees that one checkbox, worth 1 point. So under the original weights, *Gym Hero* came in **2nd**, ahead of *Rooftop Lights*, a genuinely happy song that lost 2 points only because it's labeled "indie pop" instead of "pop." After the weight shift (genre now worth less), *Rooftop Lights* moved up to 2nd and *Gym Hero* dropped to 3rd, which is closer to what a happy-pop listener probably wants.

### Comparing profiles side by side

Each comment compares two profiles' top 5 results (current weights) and explains why the difference makes sense.

- **Happy Pop Fan vs. Gym Goer.** Both lists are full of loud, electronic songs, but the pop fan's #1 is the sunny *Sunrise City* while the gym goer's is the EDM track *Pulse Reactor*. They want similar energy (0.8 vs 0.95), so their lists overlap (*Gym Hero*, *Fiesta en la Calle*). Genre and mood are what separate their top picks.
- **Chill Studier vs. Gym Goer.** These are complete opposites with no songs in common. The studier gets soft, acoustic lofi (*Library Rain*, *Midnight Coding*), and the gym goer gets fast electronic tracks. This makes sense: their energy targets (0.35 vs 0.95) are far apart, and one likes acoustic sound while the other doesn't.
- **Chill Studier vs. Classical Listener.** Both get quiet, acoustic music and share three songs (*Spacewalk Thoughts*, *Library Rain*, *Coffee Shop Stories*). The studier's list is mostly lofi because lofi has 3 songs, and the classical fan gets one classical song and then other calm songs as filler. Valid output, but it shows how thin some genres are.
- **Headbanger vs. Gym Goer.** Different #1 (*Iron Tide* vs *Pulse Reactor*), but both top 5s contain the exact same five songs, just in a different order: metal, EDM, rock, pop and latin. Once each user's one genre song is used up, both are just "people who want 0.9+ energy," and the system can't tell them apart.
- **Sad Folk Fan vs. Sad but Hyped.** Both asked for "sad," but only the folk fan gets *Letters I Never Sent*. The folk fan also asked for low energy and acoustic sound, which matches that song. The "hyped" user asked for 0.9 energy, which overrides mood, so they get upbeat pop instead. This shows the system judges by energy first and feeling second.
- **Happy Pop Fan vs. Caps Lock Pop Fan.** They have identical taste, but capital letters change the results. The real fan's #1 scores 6.92 / 7, while the caps-lock fan's best is 4.92 and ties with a hip hop song. The system can't tell "Pop" and "pop" are the same word, which is a bug, not a taste difference.
- **Classical Listener vs. Conflicted Listener.** They get the exact same top 5 in the same order, even though the Conflicted Listener said their favorite genre is metal. Their other three preferences (peaceful, low energy, acoustic) all point to classical-style music, and those together outweigh the one genre point. It makes sense for the mood they described, but their stated genre is ignored.
- **Late Night R&B vs. Country Roads.** Both want medium energy (0.5) but get different #1s (*Velvet Hours* vs *Dusty Porch Swing*). The country fan likes acoustic sound, so their filler is soft blues and lofi. The R&B fan doesn't, so their filler is synthwave and indie pop. The acoustic preference is the main thing deciding songs 2 to 5 here.
- **Hip Hop Head vs. Party Starter.** Both want upbeat, non-acoustic music around 0.75 to 0.85 energy, and they share three songs (*Sunrise City*, *Concrete Crown*, *Fiesta en la Calle*). Each gets their own genre's song at #1, and the rest is the same high-energy pool. Energy is the main thing deciding the filler.
- **Ghost Genre vs. Caps Lock Pop Fan.** One asked for a genre that doesn't exist (k-pop) and the other misspelled a real one, and both get a list built only from energy and sound. Neither gets any warning that their genre was never found.


### Adversarial / edge-case profiles

To see if the scoring logic could be "tricked," I added profiles to `ADVERSARIAL_PROFILES` in `src/main.py` with conflicting preferences, labels that don't exist, bad input, and borderline values. Each was run with `python main.py` from the `src` folder. The top 5 results are below exactly as printed in the terminal.

> **Note:** these outputs were captured with the **original weights** (genre 2.0, energy 2.0, max 6.0), before the weight-shift experiment below. The experiment section shows how each one changed.

| Profile | What it tests | Tricked? |
|---|---|---|
| Sad but Hyped | Conflicting mood and energy (pop, **sad**, energy **0.9**). | Yes: mood ignored |
| Ghost Genre | Genre and mood that don't exist in the catalog (k-pop, dreamy). | Yes: no warning, low-confidence picks |
| Caps Lock Pop Fan | Same taste as *Happy Pop Fan*, typed as "Pop" / "Happy". | Yes: case breaks matching |
| Below Zero Energy | Out-of-range energy target (-1.0). | Partly: negative scores |
| Unplugged Metalhead | Wants acoustic metal (metal, angry, 0.95 energy, likes acoustic). | Partly: odd filler picks |
| Perfectly Average | Middle energy (0.5), blues genre with a happy mood. | Yes: genre beats opposite mood |
| Conflicted Listener | Already in `USER_PROFILES`: metal fan who wants peaceful, low-energy, acoustic music. | No: sensible, but genre loses |

#### 1. Sad but Hyped

**Setup:** Conflicting mood and energy (pop, **sad**, energy **0.9**).

```
============================================================
 Sad but Hyped
 genre: pop | mood: sad | energy: 0.90 | acoustic: no
============================================================

 1. Gym Hero (Max Pulse)
    Score: 4.94 / 6.00
    Reasons:
      - genre match: pop (+2.0)
      - energy 0.93 vs target 0.90 (+1.94)
      - non-acoustic sound: 0.05 (+1.0)

 2. Sunrise City (Neon Echo)
    Score: 4.84 / 6.00
    Reasons:
      - genre match: pop (+2.0)
      - energy 0.82 vs target 0.90 (+1.84)
      - non-acoustic sound: 0.18 (+1.0)

 3. Storm Runner (Voltline)
    Score: 2.98 / 6.00
    Reasons:
      - energy 0.91 vs target 0.90 (+1.98)
      - non-acoustic sound: 0.10 (+1.0)

 4. Pulse Reactor (Kilowatt Kids)
    Score: 2.90 / 6.00
    Reasons:
      - energy 0.95 vs target 0.90 (+1.90)
      - non-acoustic sound: 0.02 (+1.0)

 5. Fiesta en la Calle (Los Brillantes)
    Score: 2.88 / 6.00
    Reasons:
      - energy 0.84 vs target 0.90 (+1.88)
      - non-acoustic sound: 0.38 (+1.0)
```

**What happened:** The mood preference is ignored. The only sad song in the catalog, *Letters I Never Sent* (folk, energy 0.26), doesn't make the top 5. Its +1.0 mood bonus can't make up for losing about 1.3 energy points and the non-acoustic point. The user gets upbeat pop and workout songs instead. Energy (up to 2.0) plus sound (1.0) outweighs mood (1.0), so when they conflict, mood loses.

#### 2. Ghost Genre

**Setup:** Genre and mood that don't exist in the catalog (k-pop, dreamy).

```
============================================================
 Ghost Genre
 genre: k-pop | mood: dreamy | energy: 0.60 | acoustic: no
============================================================

 1. Night Drive Loop (Neon Echo)
    Score: 2.70 / 6.00
    Reasons:
      - energy 0.75 vs target 0.60 (+1.70)
      - non-acoustic sound: 0.22 (+1.0)

 2. Rooftop Lights (Indigo Parade)
    Score: 2.68 / 6.00
    Reasons:
      - energy 0.76 vs target 0.60 (+1.68)
      - non-acoustic sound: 0.35 (+1.0)

 3. Concrete Crown (Block Theory)
    Score: 2.64 / 6.00
    Reasons:
      - energy 0.78 vs target 0.60 (+1.64)
      - non-acoustic sound: 0.12 (+1.0)

 4. Sunrise City (Neon Echo)
    Score: 2.56 / 6.00
    Reasons:
      - energy 0.82 vs target 0.60 (+1.56)
      - non-acoustic sound: 0.18 (+1.0)

 5. Fiesta en la Calle (Los Brillantes)
    Score: 2.52 / 6.00
    Reasons:
      - energy 0.84 vs target 0.60 (+1.52)
      - non-acoustic sound: 0.38 (+1.0)
```

**What happened:** Nothing errors or warns. The system confidently returns a top 5 that scores at most 3.0 / 6.0, based only on energy and sound. A user can't tell from the output that their genre and mood were never matched.

#### 3. Caps Lock Pop Fan

**Setup:** Same taste as *Happy Pop Fan*, typed as "Pop" / "Happy".

```
============================================================
 Caps Lock Pop Fan
 genre: Pop | mood: Happy | energy: 0.80 | acoustic: no
============================================================

 1. Concrete Crown (Block Theory)
    Score: 2.96 / 6.00
    Reasons:
      - energy 0.78 vs target 0.80 (+1.96)
      - non-acoustic sound: 0.12 (+1.0)

 2. Sunrise City (Neon Echo)
    Score: 2.96 / 6.00
    Reasons:
      - energy 0.82 vs target 0.80 (+1.96)
      - non-acoustic sound: 0.18 (+1.0)

 3. Fiesta en la Calle (Los Brillantes)
    Score: 2.92 / 6.00
    Reasons:
      - energy 0.84 vs target 0.80 (+1.92)
      - non-acoustic sound: 0.38 (+1.0)

 4. Rooftop Lights (Indigo Parade)
    Score: 2.92 / 6.00
    Reasons:
      - energy 0.76 vs target 0.80 (+1.92)
      - non-acoustic sound: 0.35 (+1.0)

 5. Night Drive Loop (Neon Echo)
    Score: 2.90 / 6.00
    Reasons:
      - energy 0.75 vs target 0.80 (+1.90)
      - non-acoustic sound: 0.22 (+1.0)
```

**What happened:** Capital letters break the matching. *Sunrise City* falls from 5.96 to 2.96 and ties with a hip hop song. *Gym Hero* (pop) drops out of the top 5 entirely. The tie is broken alphabetically, so *Concrete Crown* is ranked #1 by title order, not by fit.



### Weight-shift experiment (Step 3)

**What I changed.** I doubled the importance of energy and halved the importance of genre in `src/recommender.py`:

| Check | Before | After |
|---|---|---|
| Genre match | +2.0 | **+1.0** |
| Mood match | +1.0 | +1.0 |
| Energy closeness | 0 to +2.0 | **0 to +4.0** |
| Sound (acoustic) match | +1.0 | +1.0 |
| **Maximum score** | 6.0 | **7.0** |

**Logic changes in the code**

1. The weights are now named constants (`GENRE_WEIGHT`, `MOOD_WEIGHT`, `ENERGY_WEIGHT`, `ACOUSTIC_WEIGHT`) and `MAX_SCORE` is calculated as their sum, so the "/ 7.00" shown in the terminal always matches the real maximum.
2. Energy points are now `ENERGY_WEIGHT × max(0, 1 − gap)`. The `max(0, …)` was added because with a bigger energy weight, an out-of-range target (like −1.0) would push scores even further below zero. Now every score stays between 0 and 7.
3. The `Recommender` class (used by the tests) now uses the same `score_song` logic instead of the starter placeholder.

**Checking the math.** `tests/test_scoring.py` confirms a perfect match scores exactly 7.0, a total mismatch scores exactly 0.0, energy points shrink evenly (a 0.5 gap gives 2.0 points, a 0.1 gap gives 3.6), negative targets never give negative points, and every song stays within 0 to 7 for many different users. All 18 tests pass.

**Example: Happy Pop Fan with the new weights**

```
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

**What changed across all 17 profiles**

| Profile | Top 5 before → after | Better or just different? |
|---|---|---|
| Happy Pop Fan | *Rooftop Lights* (happy) moved above *Gym Hero* (intense) | **Better**: the happier song now ranks higher |
| Perfectly Average | *Rooftop Lights* (happy) took #1 from *Rainy Highway Blues* (melancholic) | **Better**: the user asked for happy, and genre no longer overrules that |
| Unplugged Metalhead | Calm country/blues filler replaced by loud EDM/rock/pop | **Different**: closer in energy, but further from "acoustic" |
| Late Night R&B | *Dusty Porch Swing* (country) replaced *Sunrise City* at #4 | **Different**: just a closer energy number, not a better fit |
| Below Zero Energy | Last two songs changed, and many scores now tie | **Different**: caused by the new 0-floor on energy, not the weight change |
| Other 12 profiles | Same 5 songs in the same order, only the scores went up | **Same** |

**Verdict: mostly just different, a little more accurate in a few spots.** In 12 of 17 profiles the order didn't change at all, because the #1 song already matched on everything and the filler was already sorted by energy. The two real improvements (Happy Pop Fan, Perfectly Average) happened because a weaker genre bonus let mood count for more. But the change also made the energy bubble stronger. Energy is now more than half of the score, so a user's genre matters less, and "Sad but Hyped" still never gets a sad song. A better fix would be to make mood count for more, rather than making energy even more dominant.

---

## 8. Future Work  

1. **Give partial credit for similar labels.** "Indie pop" should count a little for a pop fan. "Melancholic" should count for someone who wants "sad." I'd also ignore capital letters, so "Pop" and "pop" match.
2. **Make mood count more, and use valence.** Right now mood is worth 1 point out of 7, so energy drowns it out. I'd raise the mood weight and use valence (how positive a song sounds) as a second mood signal. That would help users like "Sad but Hyped."
3. **Add variety to the top 5.** I'd limit how often the same artist or genre appears in one list. I'd also give a small bonus to songs that don't show up for everyone, so *Fiesta en la Calle* stops being in almost every list.

Smaller ideas: warn the user when their genre or mood isn't in the catalog, and add more songs so each genre has more than one.

---

## 9. Personal Reflection  

**Biggest learning moment.** I learned that recommender systems come in two main types. Collaborative filtering recommends what similar users like. Content-based filtering compares the songs themselves to what one user says they like. Mine is content-based. My biggest learning moment came from the edge-case tests. My scoring rule looked fair on paper, but a user who wanted "sad" songs with high energy never got a sad song. That showed me a simple point system can quietly ignore part of what a user asks for.

**How AI tools helped, and when I double-checked.** I used AI to understand the requirements and to help write some of the code. It worked best after I had clearly defined the inputs, the outputs, and how the system should behave. Then I tested it to check what it actually did. I also used AI to come up with edge-case user profiles to stress-test the system. I didn't just trust the AI's description of the results. I ran the recommender myself and compared the terminal output to what was written. I also used automated tests to confirm the math stayed valid after changing the weights.

**What surprised me.** The algorithm is just adding up points from four checks. But the results still *feel* like real recommendations. The #1 song was right for every normal listener, and each pick came with reasons that sounded sensible. The simplicity also showed up as odd results, like *Gym Hero* (an intense workout song) being recommended to someone who wanted happy pop. A list can look smart while the logic behind it is very basic.

**What I'd try next.** I would add more songs, so each genre has more than one and the energy levels are more balanced. I would also improve the scoring rule. The basic point-weight system has a few biases: energy outweighs mood, exact text matching misses similar labels, and the same few songs show up for almost everyone. Fixing those would make the recommendations fairer and more varied.
