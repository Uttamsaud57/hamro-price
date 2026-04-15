"""
scraper.py – Fetch live prices from Nepali e-commerce sites.

Each scraper function returns a list of dicts:
  { 'name': str, 'price': float, 'link': str, 'seller': str }

NOTE: Web scraping depends on site structure. If a site updates its HTML,
the selectors below may need updating. Always respect robots.txt.
"""

import re
import requests
from bs4 import BeautifulSoup

# Rotate user-agent to reduce blocking
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
}

TIMEOUT = 10  # seconds


def _get(url):
    """Safe GET with timeout and error handling."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser')
    except Exception as e:
        print(f'[Scraper] Error fetching {url}: {e}')
        return None


def _parse_price(text):
    """Extract numeric price from a string like 'Rs. 62,000' → 62000.0"""
    digits = re.sub(r'[^\d.]', '', text)
    try:
        return float(digits)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Daraz Nepal
# ---------------------------------------------------------------------------
def scrape_daraz(query):
    """Search Daraz Nepal and return top product results."""
    url = f'https://www.daraz.com.np/catalog/?q={query.replace(" ", "+")}'
    soup = _get(url)
    if not soup:
        return []

    results = []
    # Daraz renders product cards with these classes (may change)
    cards = soup.select('div[data-qa-locator="product-item"]')[:5]

    for card in cards:
        try:
            name_el = card.select_one('.title--wFj93')
            price_el = card.select_one('.price--NVB62 span')
            link_el = card.select_one('a')

            if not (name_el and price_el and link_el):
                continue

            price = _parse_price(price_el.get_text())
            if not price:
                continue

            link = link_el.get('href', '')
            if link.startswith('//'):
                link = 'https:' + link

            results.append({
                'name': name_el.get_text(strip=True),
                'price': price,
                'link': link,
                'seller': 'Daraz Nepal'
            })
        except Exception:
            continue

    return results


# ---------------------------------------------------------------------------
# SastoDeal
# ---------------------------------------------------------------------------
def scrape_sastodeal(query):
    """Search SastoDeal and return top product results."""
    url = f'https://www.sastodeal.com/catalogsearch/result/?q={query.replace(" ", "+")}'
    soup = _get(url)
    if not soup:
        return []

    results = []
    cards = soup.select('li.item.product')[:5]

    for card in cards:
        try:
            name_el = card.select_one('.product-item-link')
            price_el = card.select_one('.price')
            link_el = card.select_one('a.product-item-link')

            if not (name_el and price_el and link_el):
                continue

            price = _parse_price(price_el.get_text())
            if not price:
                continue

            results.append({
                'name': name_el.get_text(strip=True),
                'price': price,
                'link': link_el.get('href', ''),
                'seller': 'SastoDeal'
            })
        except Exception:
            continue

    return results


# ---------------------------------------------------------------------------
# Unified search — runs all scrapers and merges results
# ---------------------------------------------------------------------------
def search_all(query):
    """
    Run all scrapers for a query.
    Returns merged list sorted by price ascending.
    Falls back to empty list if all scrapers fail.
    """
    all_results = []
    all_results.extend(scrape_daraz(query))
    all_results.extend(scrape_sastodeal(query))

    # Sort cheapest first
    all_results.sort(key=lambda x: x['price'])
    return all_results
