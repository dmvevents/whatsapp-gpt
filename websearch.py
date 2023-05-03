from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from typing import Dict, List

BASE_URL = "https://lite.duckduckgo.com"

class SearchResult:
    def __init__(self, title: str, body: str, url: str):
        self.title = title
        self.body = body
        self.url = url

def format_sources(filtered_sources: List[Dict[str, str]]) -> str:
    formatted_sources = []
    for source in filtered_sources:
        formatted_source = f"{source['title']} ({source['href']}):\n{source['body']}\n"
        formatted_sources.append(formatted_source)
    return '\n'.join(formatted_sources)

def get_html(query: str):
    timerange = ""
    region = "wt-wt"


    response =  ddg(keywords, region=region, safesearch='Off')

    if not response.ok:
        raise Exception(f"Failed to fetch: {response.status_code} {response.reason}")

    return {"status": response.status_code, "html": response.text, "url": response.url}

def html_to_search_results(html: str) -> List[SearchResult]:
    numResults = 3
    soup = BeautifulSoup(html, "html.parser")
    results = []

    tables = soup.find_all("table")

    if not tables:
        return results

    numTables = len(tables)
    zeroClickLink = tables[-1].find("a", rel="nofollow")

    if zeroClickLink:
        results.append(SearchResult(
            title=zeroClickLink.text,
            body=tables[1].find_all("tr")[1].text.strip(),
            url=zeroClickLink["href"]
        ))

    upperBound = numResults - 1 if zeroClickLink else numResults
    webLinks = tables[-1].select(".result-link")[:upperBound]
    webSnippets = tables[-1].select(".result-snippet")[:upperBound]

    for i, link in enumerate(webLinks):
        snippet = webSnippets[i].text.strip()

        results.append(SearchResult(
            title=link.text,
            body=snippet,
            url=link["href"]
        ))

    return results

def web_search(search: str):
    response = get_html(search)

    results = []

    if response["url"] == f"{BASE_URL}/lite/":
        results = html_to_search_results(response["html"])

    return results
