@app.route("/search", methods=["GET"])
def search():
    """
    GET /search?q=Liquid+IV+Hydration+Sticks
    Returns: JSON of query + first 5 Google/Bing results via a fallback API
    """
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Use DuckDuckGo's lite JSON API instead of the HTML page
    api_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}&format=json&no_redirect=1"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(api_url, headers=headers, timeout=10)
        data = r.json()
    except Exception as e:
        return jsonify({"query": query, "results": [], "error": str(e)}), 500

    results = []

    # Try extracting from different fields in the JSON payload
    for item in data.get("RelatedTopics", []):
        if "FirstURL" in item:
            results.append(item["FirstURL"])
        elif "Topics" in item:  # nested topics
            for sub in item["Topics"]:
                if "FirstURL" in sub:
                    results.append(sub["FirstURL"])

    # Trim and filter
    clean = [u for u in results if u.startswith("http")][:5]
    return jsonify({"query": query, "results": clean})
