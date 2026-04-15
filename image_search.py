"""
image_search.py – Match an uploaded image to products.

Phase 1 (now):  Keyword matching from filename + basic image color analysis.
Phase 2 (later): Swap match() with OpenCV feature matching or a TensorFlow
                 image embedding model.
"""

import os
import re
from PIL import Image


# Keywords mapped to product name fragments
# Extend this dict as you add more products
KEYWORD_MAP = {
    'samsung': 'samsung',
    'iphone': 'iphone',
    'apple': 'iphone',
    'sony': 'sony',
    'headphone': 'sony',
    'laptop': 'laptop',
    'hp': 'hp',
    'phone': 'samsung',
    'mobile': 'samsung',
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _keywords_from_filename(filename):
    """Extract words from filename, ignoring extension and separators."""
    name = os.path.splitext(filename)[0]
    words = re.split(r'[\s_\-\.]+', name.lower())
    return words


def _dominant_color_hint(filepath):
    """
    Very basic: returns a color label from the image's average color.
    Used as a weak secondary signal (not critical for matching).
    """
    try:
        img = Image.open(filepath).convert('RGB').resize((50, 50))
        pixels = list(img.getdata())
        avg_r = sum(p[0] for p in pixels) / len(pixels)
        avg_g = sum(p[1] for p in pixels) / len(pixels)
        avg_b = sum(p[2] for p in pixels) / len(pixels)

        if avg_r > 180 and avg_g < 100 and avg_b < 100:
            return 'red'
        elif avg_r < 100 and avg_g < 100 and avg_b > 180:
            return 'blue'
        elif avg_r > 180 and avg_g > 180 and avg_b > 180:
            return 'white'
        elif avg_r < 80 and avg_g < 80 and avg_b < 80:
            return 'black'
        else:
            return 'unknown'
    except Exception:
        return 'unknown'


def match_products(filepath, filename, products):
    """
    Match uploaded image to products.

    Args:
        filepath: absolute path to saved upload
        filename: original filename from user
        products: list of Product model objects

    Returns:
        List of (product, score) tuples sorted by score descending.
        Score is 0–100 (higher = better match).
    """
    words = _keywords_from_filename(filename)
    color = _dominant_color_hint(filepath)

    scored = []
    for product in products:
        score = 0
        product_name_lower = product.name.lower()

        # --- Filename keyword match (primary signal) ---
        for word in words:
            if len(word) < 3:
                continue
            if word in product_name_lower:
                score += 40  # direct word hit
            elif word in KEYWORD_MAP:
                mapped = KEYWORD_MAP[word]
                if mapped in product_name_lower:
                    score += 25  # indirect keyword hit

        # --- Color hint (weak secondary signal) ---
        if color in ('black', 'white') and any(
            kw in product_name_lower for kw in ['phone', 'laptop', 'headphone', 'samsung', 'iphone', 'sony', 'hp']
        ):
            score += 5

        if score > 0:
            scored.append((product, min(score, 100)))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
