from flask import Flask
from config import Config
from extensions import db, login_manager, mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.product import product_bp
    from routes.admin import admin_bp
    from routes.user import user_bp
    from routes.review import review_bp
    from routes.image_search import image_bp
    from routes.compare import compare_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(product_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(compare_bp)

    # User loader for Flask-Login
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    # Create tables and seed dummy data on first run
    with app.app_context():
        db.create_all()
        seed_data()

    return app


def seed_data():
    """Insert dummy data if DB is empty."""
    from models import Product, Seller, Price, PriceHistory
    from datetime import datetime, timedelta

    if Seller.query.first():
        return  # Already seeded

    sellers = [
        Seller(name='Daraz Nepal', rating=4.2, trust_score=8.5),
        Seller(name='SastoDeal', rating=4.0, trust_score=8.0),
        Seller(name='HamroBazar', rating=3.8, trust_score=7.5),
    ]
    db.session.add_all(sellers)
    db.session.flush()

    products = [
        Product(
            name='Samsung Galaxy A55',
            description='6.6" AMOLED display, 50MP camera, 5000mAh battery.',
            image='https://via.placeholder.com/300x200?text=Samsung+A55'
        ),
        Product(
            name='Apple iPhone 15',
            description='6.1" Super Retina XDR, A16 Bionic chip, 48MP camera.',
            image='https://via.placeholder.com/300x200?text=iPhone+15'
        ),
        Product(
            name='Sony WH-1000XM5 Headphones',
            description='Industry-leading noise cancellation, 30hr battery.',
            image='https://via.placeholder.com/300x200?text=Sony+WH1000XM5'
        ),
        Product(
            name='HP Laptop 15s',
            description='Intel Core i5, 8GB RAM, 512GB SSD, Windows 11.',
            image='https://via.placeholder.com/300x200?text=HP+Laptop+15s'
        ),
    ]
    db.session.add_all(products)
    db.session.flush()

    # Prices per product per seller
    price_data = [
        # Samsung A55
        (products[0], sellers[0], 62000, 'https://daraz.com.np'),
        (products[0], sellers[1], 61500, 'https://sastodeal.com'),
        (products[0], sellers[2], 60000, 'https://hamrobazar.com'),
        # iPhone 15
        (products[1], sellers[0], 155000, 'https://daraz.com.np'),
        (products[1], sellers[1], 153000, 'https://sastodeal.com'),
        # Sony Headphones
        (products[2], sellers[0], 45000, 'https://daraz.com.np'),
        (products[2], sellers[2], 43500, 'https://hamrobazar.com'),
        # HP Laptop
        (products[3], sellers[0], 95000, 'https://daraz.com.np'),
        (products[3], sellers[1], 93000, 'https://sastodeal.com'),
        (products[3], sellers[2], 91000, 'https://hamrobazar.com'),
    ]

    for product, seller, price_val, link in price_data:
        db.session.add(Price(
            product_id=product.id,
            seller_id=seller.id,
            price=price_val,
            link=link
        ))
        # Add 5 history points per entry (simulated past prices)
        for i in range(5):
            db.session.add(PriceHistory(
                product_id=product.id,
                seller_id=seller.id,
                price=price_val + (i * 500),  # slightly higher in the past
                date=datetime.utcnow() - timedelta(days=(4 - i) * 7)
            ))

    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
else:
    # For gunicorn: gunicorn "app:app"
    app = create_app()
