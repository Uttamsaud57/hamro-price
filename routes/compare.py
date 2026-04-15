from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import Product

compare_bp = Blueprint('compare', __name__)

MAX_COMPARE = 3


@compare_bp.route('/compare')
def compare():
    ids = session.get('compare_ids', [])
    products = Product.query.filter(Product.id.in_(ids)).all() if ids else []

    # Keep order consistent with session list
    products = sorted(products, key=lambda p: ids.index(p.id))

    # Build per-product lowest price info
    price_info = {}
    for p in products:
        sorted_prices = sorted(p.prices, key=lambda x: x.price)
        price_info[p.id] = sorted_prices  # all prices sorted cheapest first

    return render_template('compare.html', products=products, price_info=price_info)


@compare_bp.route('/compare/add/<int:product_id>')
def add_to_compare(product_id):
    ids = session.get('compare_ids', [])

    if product_id in ids:
        flash('Already in compare list.', 'info')
    elif len(ids) >= MAX_COMPARE:
        flash(f'You can compare up to {MAX_COMPARE} products at a time.', 'warning')
    else:
        ids.append(product_id)
        session['compare_ids'] = ids
        flash('Added to compare.', 'success')

    # Go back to where user came from
    return redirect(request.referrer or url_for('compare.compare'))


@compare_bp.route('/compare/remove/<int:product_id>')
def remove_from_compare(product_id):
    ids = session.get('compare_ids', [])
    if product_id in ids:
        ids.remove(product_id)
        session['compare_ids'] = ids
    return redirect(url_for('compare.compare'))


@compare_bp.route('/compare/clear')
def clear_compare():
    session.pop('compare_ids', None)
    return redirect(url_for('compare.compare'))
