"""
image_search.py – Match uploaded image to products.

Phase 1 (now):
  - Filename keyword matching (primary signal)
  - Color histogram similarity via Pillow (secondary signal)
  - Keyword map for common Nepali market products

Phase 2 (later): Replace match() with OpenCV SIFT/ORB or
                 a TensorFlow MobileNet embedding model.
"""

import os
import re
from PIL import Image

KEYWORD_MAP = {
    'samsung': 'samsung', 'galaxy': 'samsung',
    'iphone': 'iphone', 'apple': 'iphone',
    'sony': 'sony', 'headphone': 'sony', 'wh': 'sony',
    'laptop': 'laptop', 'hp': 'hp', 'notebook': 'laptop',
    'phone': 'samsung', 'mobile': 'samsung', 'smartphone': 'samsung',
    'watch': 'watch', 'tablet': 'tablet', 'ipad': 'tablet',
    'camera': 'camera', 'canon': 'camera', 'nikon': 'camera',
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# Verified marketplaces — used for trust scoring
VERIFIED_SELLERS = {'daraz nepal', 'sastodeal'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _keywords_from_filename(filename):
    name = os.path.splitext(filename)[0]
    return re.split(r'[\s_\-\.]+', name.lower())


def _color_histogram(filepath, bins=8):
    """Return a normalized RGB histogram as a flat list."""
    try:
        img = Image.open(filepath).convert('RGB').resize((64, 64))
        r, g, b = img.split()
        hist = []
        for channel in (r, g, b):
            h = channel.histogram()
            # Bin into `bins` buckets
            bucket_size = 256 // bins
            bucketed = [
                sum(h[i:i + bucket_size])
                for i in range(0, 256, bucket_size)
            ]
            total = sum(bucketed) or 1
            hist.extend([v / total for v in bucketed])
        return hist
    except Exception:
        return []


def _histogram_similarity(h1, h2):
    """Intersection similarity between two histograms (0–1)."""
    if not h1 or not h2 or len(h1) != len(h2):
        return 0.0
    return sum(min(a, b) for a, b in zip(h1, h2))


def match_products(filepath, filename, products):
    """
    Match uploaded image to products.
    Returns list of (product, score) sorted by score descending.
    Score 0–100.
    """
    words = _keywords_from_filename(filename)
    upload_hist = _color_histogram(filepath)

    scored = []
    for product in products:
        score = 0
        name_lower = product.name.lower()

        # --- Filename keyword match (primary) ---
        for word in words:
            if len(word) < 3:
                continue
            if word in name_lower:
                score += 45
            elif word in KEYWORD_MAP and KEYWORD_MAP[word] in name_lower:
                score += 28

        # --- Color histogram similarity against product image (secondary) ---
        if product.image and upload_hist:
            try:
                import urllib.request
                import tempfile
                # Only compare if image is a URL (skip placeholders)
                if product.image.startswith('http'):
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                        urllib.request.urlretrieve(product.image, tmp.name)
                        prod_hist = _color_histogram(tmp.name)
                        os.unlink(tmp.name)
                    sim = _histogram_similarity(upload_hist, prod_hist)
                    score += int(sim * 20)  # max +20 from color
            except Exception:
                pass

        if score > 0:
            scored.append((product, min(score, 100)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
