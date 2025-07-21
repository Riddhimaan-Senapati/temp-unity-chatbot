import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

MASTER_PAGE_URL = "https://docs.unity.rc.umass.edu/documentation/toc/"
HEADERS = {
    "User-Agent": "MyFriendlyWebScraper/1.0 (riddhimaan22@gmail.com)"  # Be a good bot!
}
REQUEST_DELAY_SECONDS = 0  # Time to wait between requests to be polite

# Derive the netloc (domain) from the master page URL to stay on the same site
MASTER_NETLOC = urlparse(MASTER_PAGE_URL).netloc
# Define the specific prefix for dataset paths to block
DATASETS_PATH_PREFIX_TO_BLOCK = (
    "https://docs.unity.rc.umass.edu/documentation/datasets/"
)
# The allowed datasets page
ALLOWED_DATASETS_PAGE = "https://docs.unity.rc.umass.edu/documentation/datasets"

# Defines a list of .edu domains to explicitly block
BLOCKED_EDU_DOMAINS = [
    "www.mtholyoke.edu",
    "www.smith.edu",
    "www.umass.edu",
    "www.umassd.edu",
    "www.umb.edu",
    "www.uml.eduwww.uri.edu",
    # Add more domains as needed, when more universities join or their .edu links end up in the documentation
]


# --- Helper Functions ---


def fetch_html(url):
    """Fetches HTML content from a URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_links_from_html(html_content, base_url):
    """
    Extracts all absolute HTTP/HTTPS links from HTML content,
    applying specific filtering rules.
    """
    soup = BeautifulSoup(html_content, "lxml")
    links = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        absolute_url = urljoin(base_url, href)
        absolute_url = urlparse(absolute_url)._replace(fragment="").geturl()

        parsed_url = urlparse(absolute_url)

        # Rule 1: Must be http or https
        if parsed_url.scheme not in ["http", "https"]:
            # print(f"Skipping (non-http/s): {absolute_url}")
            continue

        # Rule 2: Stay on the same primary domain as the MASTER_PAGE_URL
        if parsed_url.netloc != MASTER_NETLOC:
            # print(f"Skipping (external domain: {parsed_url.netloc} != {MASTER_NETLOC}): {absolute_url}")
            continue

        # Rule 3: Specific datasets path filtering
        if absolute_url.startswith(DATASETS_PATH_PREFIX_TO_BLOCK):
            # print(f"Skipping (datasets prefix rule): {absolute_url}")
            continue
        if absolute_url == ALLOWED_DATASETS_PAGE:
            pass
        elif absolute_url.startswith(
            "https://docs.unity.rc.umass.edu/documentation/datasets/"
        ):
            if absolute_url != ALLOWED_DATASETS_PAGE:
                # print(f"Skipping (specific datasets sub-path): {absolute_url}")
                continue

        # Rule 4:  Don't scrape links from a specific list of .edu domains
        if BLOCKED_EDU_DOMAINS and parsed_url.netloc in BLOCKED_EDU_DOMAINS:
            # print(f"Skipping (blocked .edu domain: {parsed_url.netloc}): {absolute_url}")
            continue

        links.add(absolute_url)

    return list(links)


def extract_text_content(html_content):
    """
    Extracts textual content from HTML.
    """
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "lxml")
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    text_content_div = soup.find("div", id="content")
    if text_content_div is None:
        return ""
    text = text_content_div.get_text(separator=" ", strip=True)
    return text


def filename_from_url(url):
    filename_base = url.replace("https://", "").replace("http://", "")
    filename_base = "".join(c if c not in ["/"] else "!" for c in filename_base)
    filename = filename_base + ".md"
    return filename
