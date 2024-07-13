import os
import requests
from newspaper import Article


def read_webpage(url: str, limit: int = 10000):
    """Read the text from a webpage (with an optional character limit)."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text[:limit] + ("..." if len(article.text) > limit else "")
    except:
        return "Unable to read the webpage."


def search_web(query, news: bool = False):
    """Search the web for a query. By default, returns web results. If news is set to True, returns news results instead."""
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.getenv("BRAVE_API_KEY"),
    }
    params = {"q": query}
    response = requests.get(url, headers=headers, params=params).json()

    type = "news" if news else "web"

    results = [
        {k: v for k, v in res.items() if k in ["title", "url", "description"]}
        for res in response[type]["results"]
    ]

    return results

    # Get the text from the webpages.
    for res in results:
        res["text"] = read_webpage(res["url"])

    return results


# def search_web(summary_key):
#     url = f"https://api.search.brave.com/res/v1/summarizer/search?key={summary_key}"
#     headers = {
#         'Accept': 'application/json',
#         'Accept-Encoding': 'gzip',
#         'X-Subscription-Token': os.getenv("BRAVE_API_KEY")
#     }
#     response = requests.get(url, headers=headers)
#     return response.json()
