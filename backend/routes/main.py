from flask import Blueprint, render_template, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

@main_bp.route('/shop')
def shop():
    """Render the shop page with all products."""
    product_model = current_app.config.get('product_model')
    products = product_model.get_all_products()
    return render_template('shop.html', products=products)

@main_bp.route('/contact')
def contact():
    """Render the contact page."""
    return render_template('contact.html')

@main_bp.route('/profile')
def profile():
    """Render the user profile page."""
    return render_template('profile.html')

@main_bp.route('/cart')
def cart():
    """Render the shopping cart page."""
    return render_template('cart.html')

@main_bp.route('/payment')
def payment():
    """Render the payment page."""
    return render_template('payment.html')

@main_bp.route('/order_details')
def order_details():
    """Render the order details page."""
    return render_template('order_details.html')
