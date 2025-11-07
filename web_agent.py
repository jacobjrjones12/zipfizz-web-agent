from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Zipfizz Web Agent is running!"})


@app.route("/search", methods=["GET"])
def search():
    """
    GET /search?q=Liquid+IV+Hydration+Sticks
    Returns: JSON of query + top URLs via a fallback search endpoint
    """
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # ✅ Use DuckDuckGo's HTML fallback (works without cookies/JS)
    search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for a in soup.select("a.result__a")[:5]:  # Top 5 links
            href = a.get("href")
            if href and href.startswith("http"):
                results.append(href)

        return jsonify({"query": query, "results": results})

    except Exception as e:
        return jsonify({"query": query, "results": [], "error": str(e)}), 500


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
    app.run(host="0.0.0.0", port=10000)
