# CineMatch (Flask)

Movie recommender web app (Flask) — enter 3-5 movies you've seen and get recommendations.

## Features
- Autocomplete search for movie titles (uses TMDB search)
- Aggregates TMDB's "similar movies" lists for given titles and ranks results
- Shows poster, year, genres, rating and trailer link

## Setup (local)
1. Clone/unzip the project.
2. Create a virtual environment and activate it (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate    # Windows
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and put your TMDB API key:
   ```
   TMDB_API_KEY=YOUR_KEY_HERE
   TMDB_API_URL=https://api.themoviedb.org/3
   ```
5. Run the app:
   ```bash
   python app.py
   ```
   Visit http://127.0.0.1:5000

## Notes
- This is a simple server-side implementation. For production, keep API keys secure and consider caching results (Redis) to avoid rate limits.
- The recommendation algorithm uses positional weighting on TMDB's /movie/<built-in function id>/similar results and aggregates frequency.
