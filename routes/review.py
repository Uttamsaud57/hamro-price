from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Review

review_bp = Blueprint('review', __name__)


@review_bp.route('/review/add', methods=['POST'])
@login_required
def add_review():
    seller_id = int(request.form.get('seller_id'))
    product_id = int(request.form.get('product_id'))  # used to redirect back
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment', '').strip()

    # One review per user per seller
    existing = Review.query.filter_by(
        user_id=current_user.id,
        seller_id=seller_id
    ).first()

    if existing:
        existing.rating = rating
        existing.comment = comment
        flash('Your review was updated.', 'info')
    else:
        db.session.add(Review(
            user_id=current_user.id,
            seller_id=seller_id,
            rating=rating,
            comment=comment
        ))
        flash('Review submitted!', 'success')

    # Recalculate seller average rating
    from models import Seller
    seller = Seller.query.get(seller_id)
    all_reviews = Review.query.filter_by(seller_id=seller_id).all()
    if all_reviews:
        seller.rating = round(
            sum(r.rating for r in all_reviews) / len(all_reviews), 1
        )

    db.session.commit()
    return redirect(url_for('product.product_detail', product_id=product_id))


@review_bp.route('/review/delete/<int:review_id>')
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        flash('Not allowed.', 'danger')
        return redirect(url_for('product.index'))
    product_id = request.args.get('product_id', 1)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'info')
    return redirect(url_for('product.product_detail', product_id=product_id))
