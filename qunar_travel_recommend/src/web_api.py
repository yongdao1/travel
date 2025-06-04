from flask import Flask, request, jsonify
from recommender import TravelRecommender

app = Flask(__name__)
rec = TravelRecommender("data/qunar_travel.csv")

@app.route("/api/recommend", methods=["GET"])
def recommend():
    interests = request.args.get("interests", "")
    theme = request.args.get("theme", "")
    people = request.args.get("people", "")
    city = request.args.get("city", "")
    budget = request.args.get("budget", type=float, default=None)
    top_n = request.args.get("top_n", type=int, default=5)
    recs = rec.recommend(
        interests=interests, theme=theme, people=people,
        city=city, budget=budget, top_n=top_n
    )
    return jsonify(recs)

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)