import os
from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
from dotenv import load_dotenv

load_dotenv()  # load .env if present

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_API_URL = os.getenv('TMDB_API_URL', 'https://api.themoviedb.org/3')
TMDB_IMG_BASE = 'https://image.tmdb.org/t/p/w500'

app = Flask(__name__)

if not TMDB_API_KEY:
    print('WARNING: TMDB_API_KEY not set. Copy .env.example to .env and add your key.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify(results=[])
    params = {
        'api_key': TMDB_API_KEY,
        'query': q,
        'include_adult': False,
        'language': 'en-US',
        'page': 1
    }
    try:
        r = requests.get(f"{TMDB_API_URL}/search/movie", params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return jsonify(results=data.get('results', [])[:10])
    except Exception as e:
        return jsonify(results=[])

@app.route('/recommend', methods=['POST'])
def recommend():
    payload = request.get_json() or {}
    titles = payload.get('titles') or []
    # sanitize and take up to 5
    input_titles = [t.strip() for t in titles if isinstance(t, str) and t.strip()][:5]
    if not input_titles:
        return jsonify(error='Provide 1-5 movie titles'), 400

    # Resolve titles to TMDB IDs
    ids = []
    for t in input_titles:
        try:
            r = requests.get(f"{TMDB_API_URL}/search/movie", params={
                'api_key': TMDB_API_KEY,
                'query': t,
                'include_adult': False,
                'language': 'en-US',
                'page': 1
            }, timeout=10)
            r.raise_for_status()
            sr = r.json()
            if sr.get('results'):
                ids.append(sr['results'][0]['id'])
        except Exception:
            continue

    if not ids:
        return jsonify(error='No valid movie titles found'), 400

    # Aggregate similar lists
    score_map = {}  # id -> {score, count, data}
    for movie_id in ids:
        try:
            r = requests.get(f"{TMDB_API_URL}/movie/{movie_id}/similar", params={
                'api_key': TMDB_API_KEY,
                'language': 'en-US',
                'page': 1
            }, timeout=10)
            r.raise_for_status()
            results = r.json().get('results', [])
        except Exception:
            results = []

        n = len(results) or 1
        for idx, m in enumerate(results):
            weight = (n - idx) / n  # positional weight
            mid = m.get('id')
            if not mid:
                continue
            entry = score_map.get(mid, {'score': 0.0, 'count': 0, 'data': {}})
            entry['score'] += weight
            entry['count'] += 1
            entry['data'] = {
                'id': mid,
                'title': m.get('title'),
                'poster_path': m.get('poster_path'),
                'overview': m.get('overview'),
                'release_date': m.get('release_date'),
                'vote_average': m.get('vote_average')
            }
            score_map[mid] = entry

    # Sort by score then count
    scored = sorted([{'id': k, **v} for k, v in score_map.items()], key=lambda x: (-x['score'], -x['count']))
    top = scored[:30]

    recommendations = []
    for item in top:
        try:
            dr = requests.get(f"{TMDB_API_URL}/movie/{item['id']}", params={
                'api_key': TMDB_API_KEY,
                'language': 'en-US',
                'append_to_response': 'videos,credits'
            }, timeout=10)
            dr.raise_for_status()
            d = dr.json()
        except Exception:
            continue
        vids = d.get('videos', {}).get('results', []) or []
        trailer = None
        for v in vids:
            if v.get('site') == 'YouTube' and 'trailer' in (v.get('type') or '').lower():
                trailer = v.get('key'); break
        if not trailer and vids:
            trailer = vids[0].get('key')

        recommendations.append({
            'id': d.get('id'),
            'title': d.get('title'),
            'poster_path': d.get('poster_path'),
            'overview': d.get('overview'),
            'release_date': d.get('release_date'),
            'vote_average': d.get('vote_average'),
            'genres': d.get('genres', []),
            'trailer': trailer
        })

    return jsonify(recommendations=recommendations)

# Static files route (optional)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)
