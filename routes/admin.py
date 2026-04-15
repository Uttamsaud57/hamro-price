from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Product, Seller, Price
from decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    products = Product.query.all()
    sellers = Seller.query.all()
    prices = Price.query.all()
    return render_template('admin_dashboard.html',
                           products=products, sellers=sellers, prices=prices)


@admin_bp.route('/product/add', methods=['POST'])
@login_required
@admin_required
def add_product():
    db.session.add(Product(
        name=request.form.get('name'),
        description=request.form.get('description'),
        image=request.form.get('image')
    ))
    db.session.commit()
    flash('Product added.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/product/delete/<int:pid>')
@login_required
@admin_required
def delete_product(pid):
    db.session.delete(Product.query.get_or_404(pid))
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/product/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(pid):
    product = Product.query.get_or_404(pid)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.image = request.form.get('image')
        db.session.commit()
        flash('Product updated.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('edit_product.html', product=product)


@admin_bp.route('/seller/add', methods=['POST'])
@login_required
@admin_required
def add_seller():
    db.session.add(Seller(
        name=request.form.get('name'),
        rating=float(request.form.get('rating', 0)),
        trust_score=float(request.form.get('trust_score', 0))
    ))
    db.session.commit()
    flash('Seller added.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/seller/delete/<int:sid>')
@login_required
@admin_required
def delete_seller(sid):
    db.session.delete(Seller.query.get_or_404(sid))
    db.session.commit()
    flash('Seller deleted.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/seller/edit/<int:sid>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_seller(sid):
    seller = Seller.query.get_or_404(sid)
    if request.method == 'POST':
        seller.name = request.form.get('name')
        seller.rating = float(request.form.get('rating', 0))
        seller.trust_score = float(request.form.get('trust_score', 0))
        seller.is_verified = 'is_verified' in request.form
        db.session.commit()
        flash('Seller updated.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('edit_seller.html', seller=seller)


@admin_bp.route('/price/add', methods=['POST'])
@login_required
@admin_required
def add_price():
    db.session.add(Price(
        product_id=int(request.form.get('product_id')),
        seller_id=int(request.form.get('seller_id')),
        price=float(request.form.get('price')),
        link=request.form.get('link', '')
    ))
    db.session.commit()
    flash('Price entry added.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/price/delete/<int:pid>')
@login_required
@admin_required
def delete_price(pid):
    db.session.delete(Price.query.get_or_404(pid))
    db.session.commit()
    flash('Price entry deleted.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/price/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_price(pid):
    price = Price.query.get_or_404(pid)
    if request.method == 'POST':
        price.product_id = int(request.form.get('product_id'))
        price.seller_id = int(request.form.get('seller_id'))
        price.price = float(request.form.get('price'))
        price.link = request.form.get('link', '')
        db.session.commit()
        flash('Price updated.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('edit_price.html', price=price,
                           products=Product.query.all(),
                           sellers=Seller.query.all())


@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    from models import User
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)


@admin_bp.route('/users/toggle-admin/<int:uid>')
@login_required
@admin_required
def toggle_admin(uid):
    from models import User
    user = User.query.get_or_404(uid)
    if user.id == current_user.id:
        flash("You can't change your own admin status.", 'warning')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = 'granted' if user.is_admin else 'revoked'
        flash(f'Admin access {status} for {user.name}.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/check-alerts')
@login_required
@admin_required
def check_alerts():
    from email_service import check_and_send_alerts
    from flask import current_app
    count = check_and_send_alerts(current_app._get_current_object())
    flash(f'Alert check complete. {count} email(s) sent.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/test-email')
@login_required
@admin_required
def test_email():
    from flask_mail import Message
    from extensions import mail
    try:
        msg = Message(
            subject='Hamro Price – Email Test',
            recipients=[current_user.email],
            body='Your email alerts are working correctly on Hamro Price!'
        )
        mail.send(msg)
        flash(f'Test email sent to {current_user.email}', 'success')
    except Exception as e:
        flash(f'Email failed: {e}', 'danger')
    return redirect(url_for('admin.dashboard'))
