from flask import Flask, request, jsonify
import requests, re, os
from bs4 import BeautifulSoup

app = Flask(__name__)

# ---------- health check / root route ----------

@app.route("/")
def home():
    # This is what you'll see at https://zipfizz-web-agent-real.onrender.com
    return jsonify({"status": "Zipfizz Web Agent is running!"})


# ---------- search endpoint ----------

@app.route("/search", methods=["GET"])
def search():
    """
    Example:
    GET /search?q=Liquid+IV+Hydration+Sticks
    Returns: { "query": "...", "results": ["https://...", "https://..."] }
    """
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(search_url, headers=headers, timeout=10)

    # Very simple URL extractor
    links = re.findall(r'href="(https?://[^"]+)"', r.text)
    clean = [
        l.replace("&amp;", "&")
        for l in links
        if "duckduckgo.com" not in l
        and "youtube.com" not in l
        and not any(ext in l for ext in [".jpg", ".png", ".gif", ".pdf"])
    ]

    return jsonify({"query": query, "results": clean[:5]})


# ---------- scrape endpoint ----------

@app.route("/scrape", methods=["GET"])
def scrape():
    """
    Example:
    GET /scrape?url=https://www.liquid-iv.com
    Returns: { "url": "...", "excerpt": "first 2000 chars of visible text" }
    """
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)

    soup = BeautifulSoup(r.text, "html.parser")
    text = " ".join(
        t.get_text(strip=True) 
        for t in soup.find_all(["p", "h1", "h2", "h3"])
    )

    return jsonify({"url": url, "excerpt": text[:2000]})


# ---------- main ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
