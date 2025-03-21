from flask import Blueprint, request, jsonify, current_app, session
from backend.routes.auth import login_required
import time

orders_bp = Blueprint('orders', __name__, url_prefix='/api')

@orders_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    user_id = request.user_id
    
    if 'shipping_address' not in data:
        return jsonify({'error': 'Shipping address is required'}), 400
    
    # Get cart items
    cart_model = current_app.config.get('cart_model')
    cart_items = cart_model.get_cart(user_id)
    
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Calculate total amount from cart items
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    
    # Create order
    order_model = current_app.config.get('order_model')
    order_id = order_model.create_order(
        user_id=user_id,
        items=cart_items,
        total_amount=total_amount,
        shipping_address=data['shipping_address']
    )
    
    # Clear cart after successful order
    cart_model.clear_cart(user_id)
    
    return jsonify({'message': 'Order created successfully', 'order_id': order_id}), 201

@orders_bp.route('/orders', methods=['GET'])
@login_required
def get_user_orders():
    try:
        # Get user_id from request (set by login_required decorator)
        user_id = request.user_id
        if not user_id:
            print("No user_id found in request")
            return jsonify({'error': 'User not authenticated'}), 401
            
        print(f"Fetching orders for user: {user_id}")
        
        # Get order model and fetch orders
        order_model = current_app.config.get('order_model')
        if not order_model:
            print("Order model not found in app config")
            return jsonify({'error': 'Server configuration error'}), 500
            
        # Get user orders
        orders = order_model.get_user_orders(user_id)
        print(f"Found {len(orders)} orders for user {user_id}")
        
        return jsonify(orders), 200
        
    except Exception as e:
        print(f"Error in get_user_orders: {str(e)}")
        return jsonify({'error': 'Failed to retrieve orders'}), 500

@orders_bp.route('/orders/<order_id>', methods=['GET'])
@login_required
def get_order_details(order_id):
    user_id = request.user_id
    order_model = current_app.config.get('order_model')
    order = order_model.get_order_by_id(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if str(order['user_id']) != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(order), 200

@orders_bp.route('/orders/<order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    user_id = request.user_id
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    order_model = current_app.config.get('order_model')
    order = order_model.get_order_by_id(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if str(order['user_id']) != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    valid_statuses = ['processing', 'shipped', 'delivered']
    if data['status'] not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400
    
    updated_order = order_model.update_order_status(order_id, data['status'])
    return jsonify({'message': 'Order status updated successfully', 'order': updated_order}), 200

@orders_bp.route('/orders/cod', methods=['POST'])
@login_required
def create_cod_order():
    """Create a cash on delivery order"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        required_fields = ['items', 'shippingAddress', 'total', 'subtotal', 'deliveryCharge']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get cart items to verify
        cart_model = current_app.config.get('cart_model')
        cart_items = cart_model.get_cart(user_id)
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Create order with COD payment method
        order_model = current_app.config.get('order_model')
        order_id = order_model.create_order(
            user_id=user_id,
            items=cart_items,
            total_amount=data['total'],
            shipping_address=data['shippingAddress'],
            payment_method='COD',
            payment_status='pending'
        )
        
        # Clear cart after successful order
        cart_model.clear_cart(user_id)
        
        return jsonify({
            'message': 'Order placed successfully',
            'order_id': order_id
        }), 201
    except Exception as e:
        print(f'Error creating COD order: {str(e)}')
        return jsonify({'error': 'Failed to create order'}), 500

@orders_bp.route('/orders/create-razorpay-order', methods=['POST'])
@login_required
def create_razorpay_order():
    """Create a Razorpay order for online payment"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        required_fields = ['items', 'shippingAddress', 'total', 'subtotal', 'deliveryCharge']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get cart items to verify
        cart_model = current_app.config.get('cart_model')
        cart_items = cart_model.get_cart(user_id)
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # For now, just return a mock Razorpay order ID
        # In a real implementation, you would integrate with Razorpay API
        
        return jsonify({
            'orderId': 'order_' + str(user_id) + '_' + str(int(time.time())),
            'amount': int(data['total'] * 100),  # Amount in paise
            'key': 'rzp_test_your_key_here'  # Replace with your actual test key
        }), 200
    except Exception as e:
        print(f'Error creating Razorpay order: {str(e)}')
        return jsonify({'error': 'Failed to create Razorpay order'}), 500
