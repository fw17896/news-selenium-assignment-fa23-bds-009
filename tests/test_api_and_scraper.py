import base64
import app as app_module
from news_scraper import decode_search_redirect


def test_home_page_shows_registration():
    client = app_module.app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert app_module.REGISTRATION in resp.get_data(as_text=True)


def test_missing_keyword_gives_400():
    resp = app_module.app.test_client().get("/get")
    assert resp.status_code == 400


def test_get_returns_required_fields(monkeypatch):
    class FakeScraper:
        def __init__(self, domain): pass
        def fetch_first_article(self, kw):
            return {"url": "https://www.npr.org/x",
                    "text": "Sentence one is long enough here. " * 10}
        def close(self): pass
    monkeypatch.setattr(app_module, "NewsScraper", FakeScraper)
    data = app_module.app.test_client().get("/get?keyword=ai").get_json()
    assert list(data) == ["registration", "newssource", "keyword", "url", "summary"]


def test_decode_bing_redirect():
    real = "https://www.npr.org/2026/10/01/story"
    token = "a1" + base64.urlsafe_b64encode(real.encode()).decode().rstrip("=")
    assert decode_search_redirect(f"https://www.bing.com/ck/a?!&&p=abc&u={token}&ntb=1") == real


def test_decode_duckduckgo_redirect():
    url = "//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.npr.org%2Fstory&rut=abc"
    assert decode_search_redirect(url) == "https://www.npr.org/story"


def test_plain_url_unchanged():
    assert decode_search_redirect("https://www.npr.org/a") == "https://www.npr.org/a"


def test_article_url_filter():
    from news_scraper import NewsScraper
    sc = NewsScraper.__new__(NewsScraper)
    sc.news_domain = "npr.org"
    assert sc._is_article_url("https://www.npr.org/2026/10/01/123/some-story")
    assert not sc._is_article_url("https://www.npr.org/search?query=ai")
    assert not sc._is_article_url("https://www.npr.org/")
    assert not sc._is_article_url("https://example.com/2026/10/01/x")
    assert sc._first_article(["https://www.npr.org/sections/technology/",
                              "https://www.npr.org/2026/10/01/9/x"]) == "https://www.npr.org/2026/10/01/9/x"
