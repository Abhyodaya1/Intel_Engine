import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Standard desktop browser User-Agent so bot protection headers don't reject the request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_html(html: str, char_limit: int = 4000) -> str:
    """
    DOM Normalization:
    Strips non-semantic elements that clutter the token window.
    """
    soup = BeautifulSoup(html, "html.parser")
    # Decompose removes tags and their contents entirely from the parse tree
    for tag in soup(["script", "style", "nav", "footer", "svg", "noscript"]):
        tag.decompose()
    
    # Extract visible text and normalize whitespace
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())[:char_limit]

async def fetch_page(client: httpx.AsyncClient, url: str) -> tuple[str, str, list[str]]:
    """
    Async fetch that returns: (resolved_url, extracted_text, list_of_internal_urls)
    """
    try:
        response = await client.get(url, headers=HEADERS, timeout=8.0, follow_redirects=True)
        response.raise_for_status()
    except Exception as e:
        return url, f"Fetch failure: {str(e)}", []

    soup = BeautifulSoup(response.content, "html.parser")
    discovered_links = set()
    base_domain = urlparse(url).netloc

    # Link Resolution logic
    for tag in soup.find_all("a", href=True):
        raw_href = tag["href"].strip()
        # urljoin handles:
        # "/docs" + "https://vercel.com" -> "https://vercel.com/docs"
        # "https://other.com" + "https://vercel.com" -> "https://other.com"
        full_url = urljoin(url, raw_href)
        parsed = urlparse(full_url)
        
        # Guard: Only keep http/https links belonging to the exact same domain (prevent external link drift)
        if parsed.scheme in ("http", "https") and parsed.netloc == base_domain:
            # Strip fragments (e.g., #section-title) to prevent fetching identical pages twice
            clean_link = full_url.split("#")[0]
            if clean_link != url:
                discovered_links.add(clean_link)

    return url, clean_html(response.text), list(discovered_links)

async def fetch_urls_concurrently(urls: list[str]) -> dict[str, str]:
    """
    Spawns concurrent network tasks across an asynchronous client session.
    """
    async with httpx.AsyncClient() as client:
        # Create a coroutine task for every link
        tasks = [fetch_page(client, url) for url in urls]
        # asyncio.gather executes all tasks in parallel on the event loop
        results = await asyncio.gather(*tasks)
        return {url: content for url, content, _ in results}