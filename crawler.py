import requests
import random
import logging
from bs4 import BeautifulSoup
from typing import List, Dict


def get_random_proxy(proxies: List[str]) -> Dict[str, str]:
    """Select a working proxy from the list."""
    for _ in range(len(proxies)):  # Try multiple proxies
        proxy = random.choice(proxies)
        proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        if validate_proxy(proxy):
            return proxy_dict
    logging.warning("No working proxies found, using direct connection")
    return {}


def validate_proxy(proxy: str) -> bool:
    """Check if a proxy is working."""
    test_url = "http://httpbin.org/ip"
    try:
        response = requests.get(
            test_url,
            proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            timeout=5,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def fetch_github_search_results(
    keywords: List[str], proxies: List[str], search_type: str
) -> List[Dict[str, str]]:
    """Fetch search results from GitHub using raw HTML parsing."""
    base_url = "https://github.com/search?q="
    query = "+".join(keywords)
    url = f"{base_url}{query}&type={search_type}"

    headers = {"User-Agent": "Mozilla/5.0"}
    proxy = get_random_proxy(proxies)

    try:
        response = requests.get(url, headers=headers, timeout=15, proxies=proxy)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    result_links = []

    # if search_title_div:
    for search_el in soup.find_all("div", class_="Box-sc-g0xbh4-0 gPrlij"):
        title_div = search_el.find("div", class_="Box-sc-g0xbh4-0 MHoGG search-title")
        link = title_div.find("a", class_="prc-Link-Link-85e08")
        language = search_el.find("ul", class_="bZkODq")
        if language:
            language = language.find("span")

        item = {
            "url": f"https://github.com{link['href']}",
            "extra": {
                "owner": link["href"].split("/")[1],
            },
        }
        if language:
            item["extra"]["language_details"] = {
                language.text: True
            }  # not in percentage as asked in the task bacuse it is not available in the search results

        result_links.append(item)

    return result_links


if __name__ == "__main__":
    test_input = {
        "keywords": ["python"],
        "proxies": [
            "15.72.168.208:28839",
            "114.216.205.192:8089",
            "8.217.124.178:49440",
            "91.107.130.145:11000",
            "27.79.194.183:16000",
            "3.21.101.158:3128",
            "27.79.137.254:16000",
            "149.129.226.9:80",
            "8.215.3.250:264",
            "115.72.10.52:11259",
            "193.46.0.103:3128",
            "86.106.132.194:3128",
        ],
        "search_type": "repositories",
    }

    results = fetch_github_search_results(**test_input)
    print(results)
