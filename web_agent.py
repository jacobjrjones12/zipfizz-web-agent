from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    """Simple status check route."""
    return jsonify({"status": "Zipfizz Web Agent is running!"})


@app.route("/search", methods=["GET"])
def search():
    """
    GET /search?q=Liquid+IV+Hydration+Sticks
    Returns: JSON of query + first 5 search results (using DuckDuckGo API fallback)
    """
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Use DuckDuckGo's lite JSON API instead of HTML parsing
    api_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&format=json&no_redirect=1"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(api_url, headers=headers, timeout=10)
        data = r.json()
    except Exception as e:
        return jsonify({"query": query, "results": [], "error": str(e)}), 500

    results = []
    for item in data.get("RelatedTopics", []):
        if "FirstURL" in item:
            results.append(item["FirstURL"])
        elif "Topics" in item:  # nested topics
            for sub in item["Topics"]:
                if "FirstURL" in sub:
                    results.append(sub["FirstURL"])

    # Filter and limit
    clean = [u for u in results if u.startswith("http")][:5]
    return jsonify({"query": query, "results": clean})


@app.route("/scrape", methods=["GET"])
def scrape():
    """
    GET /scrape?url=https://www.example.com
    Returns: Page title and first 500 characters of text.
    """
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string if soup.title else "No title"
        text = soup.get_text(separator=" ", strip=True)[:500]

        return jsonify({"url": url, "title": title, "preview": text})
    except Exception as e:
        return jsonify({"url": url, "error": str(e)}), 500


if __name__ == "__main__":
    # Render expects port 10000 for Python services
    app.run(host="0.0.0.0", port=10000)
