from flask import Flask, render_template
from pymongo import MongoClient
from config import Config
from backend.models.user import User
from backend.models.order import Order
from backend.models.product import Product
from backend.models.cart import Cart
from backend.models.contact import Contact

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize MongoDB connection
    client = MongoClient(app.config['MONGO_URI'])
    db = client.Readoria  # Explicitly specify database name

    # Initialize models
    user_model = User(db)
    order_model = Order(db)
    product_model = Product(db)
    cart_model = Cart(db)
    contact_model = Contact(db)
    
    # Make models available to routes
    app.config['user_model'] = user_model
    app.config['order_model'] = order_model
    app.config['product_model'] = product_model
    app.config['cart_model'] = cart_model
    app.config['contact_model'] = contact_model

    # Register blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.orders import orders_bp
    from backend.routes.products import products_bp
    from backend.routes.admin import admin_bp
    from backend.routes.main import main_bp
    from backend.routes.cart import cart_bp
    from backend.routes.contact import contact_bp
    from backend.routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(profile_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config['DEBUG'])
