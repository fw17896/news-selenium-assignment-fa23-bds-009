import os
from html import escape
from flask import Flask, jsonify, request, Response
from news_scraper import NewsScraper
from summarizer import summarize

app = Flask(__name__)
app.json.sort_keys = False  # keep keys in the order given in the assignment spec

REGISTRATION = os.getenv("REGISTRATION", "FA23-BDS-009")
NEWS_SOURCE = os.getenv("NEWS_SOURCE", "NPR")
NEWS_DOMAIN = os.getenv("NEWS_DOMAIN", "npr.org")


@app.get("/")
def home():
    """Landing web page - shows the registration number (required by the rubric)."""
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>News Summarization API - {escape(REGISTRATION)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; background:#f4f6f8; margin:0; padding:40px; }}
    .card {{ max-width:720px; margin:auto; background:#fff; padding:30px 36px;
             border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,.12); }}
    h1 {{ margin-top:0; color:#1a3d7c; }}
    .reg {{ font-size:28px; font-weight:bold; color:#c0392b; }}
    code {{ background:#eef; padding:2px 6px; border-radius:4px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>News Summarization API</h1>
    <p>Registration Number:</p>
    <p class="reg" id="registration">{escape(REGISTRATION)}</p>
    <p>News Source: <b>{escape(NEWS_SOURCE)}</b> ({escape(NEWS_DOMAIN)})</p>
    <p>Course: CSC418 - DevOps for Cloud Computing (Lab Assignment 4)</p>
    <hr>
    <p>Endpoint: <code>GET /get?keyword=your_keyword</code> (port 7000)</p>
    <p>Try it: <a href="/get?keyword=technology">/get?keyword=technology</a></p>
  </div>
</body>
</html>"""
    return Response(page, mimetype="text/html")


@app.get("/info")
def info():
    return jsonify({
        "registration": REGISTRATION,
        "newssource": NEWS_SOURCE,
        "endpoint": "/get?keyword=your_keyword",
        "port": 7000
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/get")
def get_news():
    keyword = (request.args.get("keyword") or "").strip()
    if not keyword:
        return jsonify({"error": "Missing required query parameter: keyword"}), 400

    if len(keyword) > 200:
        return jsonify({"error": "Keyword must be 200 characters or fewer"}), 400

    scraper = None
    try:
        scraper = NewsScraper(NEWS_DOMAIN)
        article = scraper.fetch_first_article(keyword)
        article_summary = summarize(article["text"])
        return jsonify({
            "registration": REGISTRATION,
            "newssource": NEWS_SOURCE,
            "keyword": keyword,
            "url": article["url"],
            "summary": article_summary
        })
    except Exception as exc:
        app.logger.exception("Unable to retrieve news article")
        return jsonify({"registration": REGISTRATION,
                        "newssource": NEWS_SOURCE,
                        "keyword": keyword,
                        "error": "Could not retrieve an article for this keyword",
                        "details": str(exc)}), 502
    finally:
        if scraper is not None:
            scraper.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=False, threaded=True)
