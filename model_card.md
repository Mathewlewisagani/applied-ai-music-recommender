# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

This is a content-based recommender. It doesn't look at what other people listen to. It compares the details of each song to what one user says they like.

**What it looks at in each song.** Every song in the catalog has a genre (like pop or folk), a mood (like happy or sad), an energy level from 0 (very calm) to 1 (very intense), and an acousticness level from 0 (electronic or heavily produced) to 1 (acoustic instruments). The catalog also lists tempo, danceability, and valence (how positive a song sounds), but the model ignores them. Tempo and danceability mostly go up and down with energy, and valence mostly follows mood, so counting them would score the same thing twice.

**What it knows about the user.** Each user has four preferences: a favorite genre, a favorite mood, how much energy they want, and whether they like acoustic music.

**How a song gets its score.** Every song starts at 0 and earns points, up to a maximum of 6:

- **2 points** if the genre is the user's favorite. Genre gets the most weight because it is the clearest sign of taste.
- **1 point** if the mood is the user's favorite.
- **Up to 2 points** for energy, based on how close the song is to the user's target. A perfect match gets 2 points, and the further away the song is, the fewer points it gets. Closeness counts, not loudness, so someone who wants calm music isn't pushed toward loud songs.
- **1 point** if the sound fits: a clearly acoustic song for a user who likes acoustic music, or a clearly non-acoustic song for a user who doesn't.

Every time a song earns points, the model writes down why (for example, "genre match: pop"), so each recommendation comes with its reasons.

**How it picks the final list.** After every song is scored, the model sorts them from highest to lowest score and shows the top 5. If two songs tie, they are listed alphabetically by title so the results are the same every time.

**Changes from the starter.** The starter code returned the first few songs in the file without scoring them. This version loads the full catalog (expanded from 10 to 20 songs with 10 new genres and moods), scores every song with the rules above, ranks them, and explains each pick.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
