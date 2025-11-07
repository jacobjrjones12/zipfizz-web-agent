from flask import Flask, request, jsonify
import requests, re
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "Zipfizz Web Agent is running!"})

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(search_url, headers=headers, timeout=10)
    links = re.findall(r'href="(https?://[^"]+)"', r.text)
    clean = [l for l in links if "duckduckgo.com" not in l and "youtube.com" not in l][:5]

    return jsonify({"query": query, "results": clean})

@app.route("/scrape", methods=["GET"])
def scrape():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    text = " ".join([t.get_text(strip=True) for t in soup.find_all(["p","h1","h2","h3"])])
    return jsonify({"url": url, "excerpt": text[:2000]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
