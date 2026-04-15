"""
Quick test — run this directly to check if scrapers are working.
Usage: python test_scraper.py
"""
from scraper import search_all

query = 'Samsung Galaxy'
print(f'Searching for: {query}\n')

results = search_all(query)

if results:
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['seller']}] {r['name']}")
        print(f"   Price: Rs. {r['price']:,.0f}")
        print(f"   Link:  {r['link'][:80]}")
        print()
else:
    print('No results. Sites may be blocking or selectors need updating.')
