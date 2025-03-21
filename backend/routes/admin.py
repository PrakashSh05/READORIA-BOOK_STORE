from flask import Blueprint, request, jsonify, session, render_template, current_app, redirect, send_from_directory
from backend.models.order import Order
from backend.models.product import Product
from backend.models.user import User
from backend.models.contact import Contact
from backend.routes.auth import login_required
from functools import wraps
import jwt
from bson import ObjectId
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid

admin_bp = Blueprint('admin', __name__)

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        # Generate a unique filename
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Save the file
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Return the URL path
        return f'/static/uploads/{unique_filename}'
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                # Try to get token from query parameters (for GET requests)
                token = request.args.get('token')
                if not token:
                    # For GET requests to /admin, redirect to login
                    if request.endpoint == 'admin_bp.admin_dashboard':
                        return redirect('/?error=no_token')
                    return jsonify({'error': 'No token provided'}), 401
            else:
                if not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Invalid token format'}), 401
                
                # Extract token
                token = auth_header.split(' ')[1]
            
            # Decode token
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Verify required claims
            if 'user_id' not in payload:
                return jsonify({'error': 'Invalid token'}), 401
                
            # Get user from database
            user_model = current_app.config.get('user_model')
            user = user_model.get_user_by_id(payload['user_id'])
            
            # Check if user is admin
            if not user or not user.get('is_admin', False):
                if request.endpoint == 'admin_bp.admin_dashboard':
                    return redirect('/?error=not_admin')
                return jsonify({'error': 'Admin access required'}), 403
            
            # Store user ID in request context
            request.user_id = payload['user_id']
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            if request.endpoint == 'admin_bp.admin_dashboard':
                return redirect('/?error=token_expired')
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            if request.endpoint == 'admin_bp.admin_dashboard':
                return redirect('/?error=invalid_token')
            return jsonify({'error': f'Invalid token: {str(e)}'}), 401
        except Exception as e:
            if request.endpoint == 'admin_bp.admin_dashboard':
                return redirect('/?error=auth_failed')
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
    return decorated_function

@admin_bp.route('/admin')
def admin_dashboard():
    """Render the admin dashboard."""
    # Check if token exists in query parameters
    token = request.args.get('token')
    if token:
        # If token exists in query, render template that will store token and redirect
        return render_template('admin_redirect.html', token=token)
    return render_template('admin.html')

@admin_bp.route('/api/admin/verify', methods=['GET'])
@admin_required
def verify_admin():
    """Verify admin access."""
    return jsonify({'message': 'Admin access verified'}), 200

@admin_bp.route('/api/admin/orders', methods=['GET'])
@admin_required
def get_all_orders():
    try:
        status = request.args.get('status')
        order_model = current_app.config.get('order_model')
        user_model = current_app.config.get('user_model')
        
        orders = order_model.get_all_orders(status)
        
        # Enhance orders with user details
        for order in orders:
            try:
                # Convert ObjectIds to strings for JSON serialization
                order['_id'] = str(order['_id'])
                user_id = order.get('user_id')
                
                # Convert user_id to string if it's an ObjectId
                if user_id:
                    if isinstance(user_id, ObjectId):
                        user_id = str(user_id)
                    order['user_id'] = user_id
                else:
                    order['user_id'] = 'N/A'
                
                # Get user details
                user = user_model.get_user_by_id(user_id) if user_id and user_id != 'N/A' else None
                
                # Set user details with proper fallbacks
                order['user_details'] = {
                    'name': user.get('name', 'N/A') if user else 'N/A',
                    'email': user.get('email', 'N/A') if user else 'N/A',
                    'phone': user.get('phone', 'N/A') if user else 'N/A'
                }
                
                # Get shipping address from order first, fall back to user's address
                shipping_address = order.get('shipping_address', {})
                if not shipping_address and user:
                    shipping_address = user.get('address', {})
                
                order['shipping_address'] = {
                    'street': shipping_address.get('street', 'N/A'),
                    'city': shipping_address.get('city', 'N/A'),
                    'state': shipping_address.get('state', 'N/A'),
                    'zipcode': shipping_address.get('zipcode', 'N/A')
                }
                
                order['total'] = float(order.get('total_amount', 0))
                order['status'] = order.get('status', 'pending')
            except Exception as e:
                print(f"Error processing order {order.get('_id')}: {str(e)}")
                # Set default values for the order that failed to process
                order['user_details'] = {'name': 'N/A', 'email': 'N/A', 'phone': 'N/A'}
                order['shipping_address'] = {'street': 'N/A', 'city': 'N/A', 'state': 'N/A', 'zipcode': 'N/A'}
                order['total'] = 0
                order['status'] = 'pending'
        
        return jsonify(orders), 200
    except Exception as e:
        print(f"Error in get_all_orders: {str(e)}")
        return jsonify({'error': 'Failed to load orders'}), 500

@admin_bp.route('/api/admin/orders/<order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400

        status = data['status']
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        
        if status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400

        # Update the status and corresponding date
        update_data = {'status': status}
        if status == 'processing':
            update_data['processing_date'] = datetime.utcnow()
        elif status == 'shipped':
            update_data['shipped_date'] = datetime.utcnow()
        elif status == 'delivered':
            update_data['delivered_date'] = datetime.utcnow()
        elif status == 'cancelled':
            update_data['cancelled_date'] = datetime.utcnow()

        order_model = current_app.config.get('order_model')
        order_model.update_order_status(order_id, update_data)
        return jsonify({'message': 'Order status updated successfully'}), 200

    except Exception as e:
        print(f"Error updating order status: {str(e)}")
        return jsonify({'error': 'Failed to update order status'}), 500

@admin_bp.route('/api/admin/products', methods=['GET'])
@admin_required
def get_all_products():
    product_model = current_app.config.get('product_model')
    products = product_model.get_all_products(request.args.get('category'))
    return jsonify(products), 200

@admin_bp.route('/api/admin/products', methods=['POST'])
@admin_required
def create_product():
    try:
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        price = request.form.get('price')
        stock = request.form.get('stock')
        
        if not all([name, description, category, price]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Handle file upload
        image_url = None
        if 'image' in request.files:
            image_url = save_uploaded_file(request.files['image'])
            if not image_url:
                return jsonify({'error': 'Invalid file type'}), 400
        
        # Create product data
        product_data = {
            'name': name,
            'description': description,
            'category': category,
            'price': float(price),
            'stock': int(stock) if stock else 0,
            'image_url': image_url
        }
        
        # Get product model and create product
        product_model = current_app.config.get('product_model')
        product_id = product_model.create_product(product_data)
        
        return jsonify({
            'message': 'Product created successfully',
            'product_id': str(product_id)
        }), 201
        
    except Exception as e:
        print(f"Error creating product: {str(e)}")
        return jsonify({'error': 'Failed to create product'}), 500

@admin_bp.route('/api/admin/products/<product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    try:
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        price = request.form.get('price')
        stock = request.form.get('stock')
        
        if not all([name, description, category, price]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create update data
        update_data = {
            'name': name,
            'description': description,
            'category': category,
            'price': float(price),
            'stock': int(stock) if stock else 0
        }
        
        # Handle file upload if present
        if 'image' in request.files:
            image_url = save_uploaded_file(request.files['image'])
            if image_url:
                update_data['image_url'] = image_url
        
        # Get product model and update product
        product_model = current_app.config.get('product_model')
        product_model.update_product(product_id, update_data)
        
        return jsonify({'message': 'Product updated successfully'}), 200
        
    except Exception as e:
        print(f"Error updating product: {str(e)}")
        return jsonify({'error': 'Failed to update product'}), 500

@admin_bp.route('/api/admin/products/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    # Get product model from current app
    product_model = current_app.config.get('product_model')
    
    # Delete product
    result = product_model.delete_product(product_id)
    
    if result.deleted_count == 0:
        return jsonify({'error': 'Product not found'}), 404
        
    return jsonify({'message': 'Product deleted successfully'}), 200

@admin_bp.route('/api/admin/products/<product_id>', methods=['GET'])
@admin_required
def get_product(product_id):
    # Get product model from current app
    product_model = current_app.config.get('product_model')
    
    # Get product by ID
    product = product_model.get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Convert ObjectId to string for JSON serialization
    product['_id'] = str(product['_id'])
    
    return jsonify(product), 200

@admin_bp.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """Get admin dashboard statistics"""
    order_model = current_app.config.get('order_model')
    contact_model = current_app.config.get('contact_model')
    
    # Get total orders
    total_orders = order_model.get_all_orders()
    
    # Get pending orders
    pending_orders = order_model.get_all_orders(status='pending')
    
    # Get unread messages
    unread_messages = contact_model.get_all_contacts(status='unread')
    
    stats = {
        'total_orders': len(total_orders),
        'pending_orders': len(pending_orders),
        'unread_messages': len(unread_messages)
    }
    
    return jsonify(stats), 200

@admin_bp.route('/api/admin/contacts', methods=['GET'])
@admin_required
def get_all_contacts():
    """Get all contact form submissions"""
    contact_model = current_app.config.get('contact_model')
    contacts = contact_model.get_all_contacts()
    
    # Convert ObjectId to string for JSON serialization
    for contact in contacts:
        contact['_id'] = str(contact['_id'])
        contact['created_at'] = contact['created_at'].isoformat()
        if contact.get('read_at'):
            contact['read_at'] = contact['read_at'].isoformat()
    
    return jsonify(contacts), 200

@admin_bp.route('/api/admin/contacts/<contact_id>/read', methods=['PUT'])
@admin_required
def mark_contact_as_read(contact_id):
    """Mark a contact message as read"""
    contact_model = current_app.config.get('contact_model')
    contact = contact_model.mark_as_read(contact_id)
    
    if contact:
        contact['_id'] = str(contact['_id'])
        contact['created_at'] = contact['created_at'].isoformat()
        if contact.get('read_at'):
            contact['read_at'] = contact['read_at'].isoformat()
        return jsonify({'message': 'Contact marked as read', 'contact': contact}), 200
    return jsonify({'error': 'Contact not found'}), 404

@admin_bp.route('/api/admin/contacts/<contact_id>', methods=['DELETE'])
@admin_required
def delete_contact(contact_id):
    """Delete a contact message"""
    contact_model = current_app.config.get('contact_model')
    result = contact_model.delete_contact(contact_id)
    
    if result.deleted_count > 0:
        return jsonify({'message': 'Contact deleted successfully'}), 200
    return jsonify({'error': 'Contact not found'}), 404 