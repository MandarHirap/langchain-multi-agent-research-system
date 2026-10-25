import os
from dotenv import load_dotenv
from tavily import TavilyClient
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def web_search(query: str) -> str:
    """Search the web for recent information and return titles, URLs, and snippets."""
    results = tavily.search(query=query, max_results=5)

    out=[]

    for r in results['results']:
        out.append(
            f"Title:{r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    return "\n".join(out)

def scrape_url(url: str) -> str:
    """Scrape a URL and extract clean, readable content using multiple strategies."""

    try:
        downloaded = trafilatura.fetch_url(url)

        if downloaded:
            content = trafilatura.extract(
                downloaded,
                include_links=False,
                include_images=False,
                favor_precision=True
            )

            if content and len(content.strip()) > 200:
                return content.strip()

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36"
            )
        }

        import requests

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        html = response.text

        document = Document(html)
        readable_html = document.summary()

        soup = BeautifulSoup(readable_html, "html.parser")

        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        content = soup.get_text(separator=" ", strip=True)
        content = re.sub(r"\s+", " ", content).strip()

        if content:
            return content

        soup = BeautifulSoup(html, "html.parser")

        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        return re.sub(r"\s+", " ", soup.get_text(separator=" ", strip=True)).strip()

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}"

    except Exception as e:
        return f"Error scraping URL: {e}"