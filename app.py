from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# Get API key from environment variables (Render)
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
TMDB_API_URL = os.environ.get("TMDB_API_URL", "https://api.themoviedb.org/3")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        # Get movie titles from the form
        movies = request.json.get("movies", [])
        recommendations = []

        # Example: return 3 top trending movies (so site loads instantly)
        url = f"{TMDB_API_URL}/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
        response = requests.get(url)
        data = response.json()
        for movie in data.get("results", [])[:5]:
            recommendations.append({
                "title": movie["title"],
                "poster": f"https://image.tmdb.org/t/p/w200{movie['poster_path']}" if movie.get("poster_path") else "",
                "url": f"https://www.themoviedb.org/movie/{movie['id']}"
            })

        return jsonify({"recommendations": recommendations})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
