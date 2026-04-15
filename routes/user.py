from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import PriceAlert, Product, Price

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile')
@login_required
def profile():
    alerts = PriceAlert.query.filter_by(user_id=current_user.id).order_by(
        PriceAlert.created_at.desc()
    ).all()

    # Check each active alert against current lowest price
    triggered = []
    for alert in alerts:
        if alert.is_active:
            min_price_row = (
                Price.query
                .filter_by(product_id=alert.product_id)
                .order_by(Price.price.asc())
                .first()
            )
            if min_price_row and min_price_row.price <= alert.target_price:
                triggered.append({
                    'alert': alert,
                    'current_price': min_price_row.price,
                    'seller': min_price_row.seller.name
                })

    return render_template('profile.html', alerts=alerts, triggered=triggered)


@user_bp.route('/alert/add', methods=['POST'])
@login_required
def add_alert():
    product_id = int(request.form.get('product_id'))
    target_price = float(request.form.get('target_price'))

    # Prevent duplicate active alerts for same product
    existing = PriceAlert.query.filter_by(
        user_id=current_user.id,
        product_id=product_id,
        is_active=True
    ).first()

    if existing:
        existing.target_price = target_price  # update instead
        flash('Alert updated.', 'info')
    else:
        db.session.add(PriceAlert(
            user_id=current_user.id,
            product_id=product_id,
            target_price=target_price
        ))
        flash('Price alert set!', 'success')

    db.session.commit()
    return redirect(url_for('product.product_detail', product_id=product_id))


@user_bp.route('/alert/delete/<int:alert_id>')
@login_required
def delete_alert(alert_id):
    alert = PriceAlert.query.get_or_404(alert_id)
    if alert.user_id != current_user.id:
        flash('Not allowed.', 'danger')
        return redirect(url_for('user.profile'))
    db.session.delete(alert)
    db.session.commit()
    flash('Alert removed.', 'info')
    return redirect(url_for('user.profile'))
