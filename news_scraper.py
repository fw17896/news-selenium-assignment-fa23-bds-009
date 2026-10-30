import base64
import re
from urllib.parse import quote_plus, urlparse, urlsplit, parse_qs, unquote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import trafilatura


def decode_search_redirect(href):
    """Turn Bing / DuckDuckGo redirect links into the real destination URL.

    Bing often returns links like  https://www.bing.com/ck/a?...&u=a1aHR0cHM6Ly8...
    DuckDuckGo returns             //duckduckgo.com/l/?uddg=https%3A%2F%2Fnpr.org%2F...
    If the link is already a normal URL, it is returned unchanged.
    """
    if not href:
        return href
    if href.startswith("//"):
        href = "https:" + href
    parts = urlsplit(href)
    host = (parts.hostname or "").lower()
    query = parse_qs(parts.query)

    # Bing redirect: 'u' parameter = "a1" + base64url(real_url)
    if host.endswith("bing.com") and parts.path.startswith("/ck/") and "u" in query:
        token = query["u"][0]
        if token.startswith("a1"):
            token = token[2:]
        try:
            token += "=" * (-len(token) % 4)
            return base64.urlsafe_b64decode(token).decode("utf-8")
        except Exception:
            return href

    # DuckDuckGo redirect: 'uddg' parameter = url-encoded real_url
    if host.endswith("duckduckgo.com") and "uddg" in query:
        return unquote(query["uddg"][0])

    return href


class NewsScraper:
    """Uses Selenium to search the assigned news domain and read the first result."""

    def __init__(self, news_domain="npr.org"):
        self.news_domain = news_domain.lower().lstrip(".")
        self.driver = self._create_driver()

    @staticmethod
    def _create_driver():
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1440,1000")
        options.add_argument("--lang=en-US")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(45)
        return driver

    def _is_assigned_domain(self, url):
        host = (urlparse(url or "").hostname or "").lower()
        return host == self.news_domain or host.endswith("." + self.news_domain)

    _DATE_PATH = re.compile(r"/\d{4}/\d{2}/\d{2}/")

    def _is_article_url(self, url):
        """True for a real article on the assigned domain (not home/search/section pages)."""
        if not self._is_assigned_domain(url):
            return False
        path = urlparse(url).path or "/"
        if "/search" in path:
            return False
        return bool(self._DATE_PATH.search(path)) or "storyId=" in (urlparse(url).query or "")

    def _collect_links(self, selector):
        """Return real (redirect-decoded) URLs for every link matching selector."""
        urls = []
        for link in self.driver.find_elements(By.CSS_SELECTOR, selector):
            href = decode_search_redirect(link.get_attribute("href"))
            if href:
                urls.append(href)
        return urls

    def _first_article(self, urls):
        for url in urls:
            if self._is_article_url(url):
                return url
        for url in urls:  # looser fallback: any non-search page of the domain
            if self._is_assigned_domain(url) and (urlparse(url).path or "/") not in ("", "/") \
                    and "/search" not in url:
                return url
        return None

    # ---- search methods (tried in order until one gives an article link) ----
    def _search_site_itself(self, keyword):
        """Use the news site's own search page (JavaScript-rendered, so Selenium is needed)."""
        self.driver.get(f"https://www.{self.news_domain}/search?query={quote_plus(keyword)}")

        def article_link(driver):
            for a in driver.find_elements(By.CSS_SELECTOR, "a[href]"):
                href = a.get_attribute("href")
                if href and self._is_article_url(href):
                    return href
            return False

        return WebDriverWait(self.driver, 25).until(article_link)

    def _search_bing(self, keyword):
        query = quote_plus(f"site:{self.news_domain} {keyword}")
        self.driver.get(f"https://www.bing.com/search?q={query}")
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.b_algo h2 a"))
        )
        urls = self._collect_links("li.b_algo h2 a") + self._collect_links("a[href]")
        return self._first_article(urls)

    def _search_duckduckgo(self, keyword):
        query = quote_plus(f"site:{self.news_domain} {keyword}")
        self.driver.get(f"https://html.duckduckgo.com/html/?q={query}")
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.result__a"))
        )
        return self._first_article(self._collect_links("a.result__a"))

    def _find_first_result(self, keyword):
        errors = []
        methods = []
        if self.news_domain == "npr.org":
            methods.append(self._search_site_itself)
        methods += [self._search_bing, self._search_duckduckgo]
        for method in methods:
            try:
                url = method(keyword)
                if url:
                    return url
                errors.append(f"{method.__name__}: no article link")
            except Exception as exc:  # try the next method
                try:
                    title = (self.driver.title or "")[:50]
                except Exception:
                    title = "?"
                errors.append(f"{method.__name__}: {type(exc).__name__} (page title: '{title}')")
        raise RuntimeError(
            f"No result from {self.news_domain} found for '{keyword}' | " + " | ".join(errors)
        )

    def fetch_first_article(self, keyword):
        article_url = self._find_first_result(keyword)
        self.driver.get(article_url)

        try:
            WebDriverWait(self.driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            pass

        html = self.driver.page_source
        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            favor_precision=True
        )

        if not text or len(text.split()) < 40:
            # Basic fallback if the article extractor cannot identify the main text.
            elements = self.driver.find_elements(By.CSS_SELECTOR, "article, main")
            text = "\n".join(element.text for element in elements if element.text.strip())

        if not text or len(text.split()) < 30:
            raise RuntimeError("The selected page did not contain enough readable article text")

        return {"url": self.driver.current_url, "text": text}

    def close(self):
        if self.driver:
            self.driver.quit()
