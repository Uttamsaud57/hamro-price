import os
from flask import Blueprint, render_template, request, current_app
from werkzeug.utils import secure_filename
from models import Product
from image_search import match_products, allowed_file

image_bp = Blueprint('image_search', __name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')


def _upload_dir():
    path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(path, exist_ok=True)
    return path


@image_bp.route('/image-search', methods=['GET', 'POST'])
def image_search():
    matches = []
    preview_url = None
    error = None

    if request.method == 'POST':
        file = request.files.get('image')

        if not file or file.filename == '':
            error = 'Please select an image file.'
        elif not allowed_file(file.filename):
            error = 'Unsupported file type. Use JPG, PNG, or WEBP.'
        else:
            filename = secure_filename(file.filename)
            save_path = os.path.join(_upload_dir(), filename)
            file.save(save_path)

            preview_url = f'/static/uploads/{filename}'
            products = Product.query.all()
            scored = match_products(save_path, filename, products)
            matches = scored  # list of (product, score)

            if not matches:
                error = 'No matching products found. Try a clearer product image.'

    return render_template('image_search.html',
                           matches=matches,
                           preview_url=preview_url,
                           error=error)
