import os
import requests
from newspaper import Article


def read_webpage(url: str, offset: int = 0, limit: int = 10000):
    """Read the text from a webpage (with an optional character limit)."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        article_text = article.text[offset : offset + limit]
        return article_text + ("..." if len(article_text) > limit else "")
    except:
        return "Unable to read the webpage."


def search_web(query):
    """Search the web for a query. By default, returns web results. If news is set to True, returns news results instead."""
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.getenv("BRAVE_API_KEY"),
    }
    params = {"q": query}
    response = requests.get(url, headers=headers, params=params).json()
    results = [
        {k: v for k, v in res.items() if k in ["title", "url", "description"]}
        for res in response["web"]["results"]
    ]
    return results
