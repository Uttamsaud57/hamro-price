from flask import Blueprint, render_template, request
from models import Product, Price, Seller, PriceHistory, Review

product_bp = Blueprint('product', __name__)


@product_bp.route('/')
def index():
    from models import Seller, Price
    featured = Product.query.limit(4).all()
    stats = {
        'products': Product.query.count(),
        'sellers': Seller.query.count(),
        'prices': Price.query.count(),
    }
    return render_template('index.html', featured=featured, stats=stats)


@product_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    pagination = None
    results = []

    if query:
        pagination = (
            Product.query
            .filter(Product.name.ilike(f'%{query}%'))
            .paginate(page=page, per_page=8, error_out=False)
        )
        results = pagination.items

    return render_template('search.html', results=results,
                           query=query, pagination=pagination)


@product_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    # Get all prices for this product, ordered cheapest first
    prices = (
        Price.query
        .filter_by(product_id=product_id)
        .join(Seller)
        .order_by(Price.price.asc())
        .all()
    )

    # Price history for Chart.js (grouped by seller)
    history_data = {}
    history_records = (
        PriceHistory.query
        .filter_by(product_id=product_id)
        .order_by(PriceHistory.date.asc())
        .all()
    )
    for record in history_records:
        seller_name = Seller.query.get(record.seller_id).name
        if seller_name not in history_data:
            history_data[seller_name] = {'dates': [], 'prices': []}
        history_data[seller_name]['dates'].append(record.date.strftime('%b %d'))
        history_data[seller_name]['prices'].append(record.price)

    # Sellers for this product (for the review form dropdown)
    seller_ids = [p.seller_id for p in prices]
    sellers = Seller.query.filter(Seller.id.in_(seller_ids)).all()

    # Reviews for sellers of this product
    reviews = (
        Review.query
        .filter(Review.seller_id.in_(seller_ids))
        .order_by(Review.id.desc())
        .all()
    )

    return render_template(
        'product.html',
        product=product,
        prices=prices,
        history_data=history_data,
        sellers=sellers,
        reviews=reviews
    )


@product_bp.route('/live-search')
def live_search():
    """Search live prices from external sites via scraper."""
    query = request.args.get('q', '').strip()
    results = []
    error = None

    if query:
        try:
            from scraper import search_all
            results = search_all(query)
        except Exception as e:
            error = f'Scraper error: {e}'

    return render_template('live_search.html', results=results,
                           query=query, error=error)
