from flask import Blueprint, request, jsonify, current_app
from backend.routes.auth import login_required

cart_bp = Blueprint('cart', __name__, url_prefix='/api')


@cart_bp.route('/cart', methods=['GET'])
@login_required
def get_cart():
    """Get the user's cart items."""
    try:
        print(f'Getting cart for user_id: {request.user_id}')
        cart_model = current_app.config.get('cart_model')
        if not cart_model:
            print('Cart model not found in config')
            return jsonify({'error': 'Cart service unavailable'}), 500
            
        cart_items = cart_model.get_cart(request.user_id)
        print(f'Retrieved cart items: {cart_items}')
        
        # Ensure we always return a list, even if cart_items is None
        if cart_items is None:
            cart_items = []
            
        return jsonify(cart_items)
    except Exception as e:
        print(f'Error getting cart: {str(e)}')
        return jsonify({'error': 'Failed to get cart items'}), 500

@cart_bp.route('/cart', methods=['POST'])
@login_required
def add_to_cart():
    """Add an item to the cart."""
    try:
        print(f'Adding to cart for user_id: {request.user_id}')
        data = request.get_json()
        if not data:
            print('No data provided in request')
            return jsonify({'error': 'No data provided'}), 400
            
        print(f'Received cart data: {data}')
        
        required_fields = ['product_id', 'name', 'price', 'quantity']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f'Missing fields: {missing_fields}')
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
        
        try:
            # Ensure price is a float
            data['price'] = float(data['price'])
            # Ensure quantity is an integer
            data['quantity'] = int(data['quantity'])
        except (ValueError, TypeError) as e:
            print(f'Invalid data format: {str(e)}')
            return jsonify({'error': 'Invalid price or quantity format'}), 400
        
        cart_model = current_app.config.get('cart_model')
        if not cart_model:
            print('Cart model not found in config')
            return jsonify({'error': 'Cart service unavailable'}), 500
            
        print('Adding item to cart with data:', data)
        cart_items = cart_model.add_item(request.user_id, data)
        
        if cart_items is None:
            print('Failed to update cart - cart_items is None')
            return jsonify({'error': 'Failed to update cart'}), 500
            
        print('Successfully added item to cart')
        return jsonify({'message': 'Cart updated successfully', 'cart': cart_items})
    except Exception as e:
        print(f'Error adding to cart: {str(e)}')
        return jsonify({'error': 'Failed to add item to cart'}), 500

@cart_bp.route('/cart', methods=['DELETE'])
@login_required
def remove_from_cart():
    """Remove an item from the cart."""
    product_id = request.args.get('product_id')
    
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400
    
    cart_model = current_app.config.get('cart_model')
    if cart_model.remove_item(request.user_id, product_id):
        cart_items = cart_model.get_cart(request.user_id)
        return jsonify({'message': 'Item removed from cart', 'cart': cart_items})
    else:
        return jsonify({'error': 'Item not found in cart'}), 404

@cart_bp.route('/cart/quantity', methods=['PUT'])
@login_required
def update_quantity():
    """Update the quantity of an item in the cart."""
    try:
        print(f'Received quantity update request for user_id: {request.user_id}')
        data = request.get_json()
        print(f'Request data: {data}')
        
        if not data:
            print('No JSON data received')
            return jsonify({'error': 'No data provided'}), 400
        
        if not all(k in data for k in ['product_id', 'quantity']):
            missing = [k for k in ['product_id', 'quantity'] if k not in data]
            print(f'Missing required fields: {missing}')
            return jsonify({'error': f'Missing required fields: {missing}'}), 400
        
        # Validate quantity is an integer
        try:
            quantity = int(data['quantity'])
            if quantity <= 0:
                print(f'Invalid quantity: {quantity}')
                return jsonify({'error': 'Quantity must be greater than 0'}), 400
        except (ValueError, TypeError):
            print(f'Invalid quantity format: {data["quantity"]}')
            return jsonify({'error': 'Quantity must be a valid integer'}), 400
        
        cart_model = current_app.config.get('cart_model')
        if not cart_model:
            print('Cart model not found in config')
            return jsonify({'error': 'Cart service unavailable'}), 500
            
        print(f'Updating quantity for product_id: {data["product_id"]} to {quantity}')
        if cart_model.update_item_quantity(request.user_id, data['product_id'], quantity):
            cart_items = cart_model.get_cart(request.user_id)
            print('Quantity updated successfully')
            return jsonify({'message': 'Quantity updated successfully', 'cart': cart_items})
        else:
            print('Failed to update quantity')
            return jsonify({'error': 'Failed to update quantity'}), 400
    except Exception as e:
        print(f'Error in update_quantity: {str(e)}')
        return jsonify({'error': 'Server error processing request'}), 500

@cart_bp.route('/cart', methods=['PUT'])
@login_required
def clear_cart():
    """Clear all items from the cart."""
    cart_model = current_app.config.get('cart_model')
    
    if cart_model.clear_cart(request.user_id):
        return jsonify({'message': 'Cart cleared successfully', 'cart': []})
    else:
        return jsonify({'error': 'Failed to clear cart'}), 400
