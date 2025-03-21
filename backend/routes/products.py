from flask import Blueprint, request, jsonify, current_app
from backend.routes.auth import login_required

products_bp = Blueprint('products', __name__, url_prefix='/api')

@products_bp.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    product_model = current_app.config.get('product_model')
    products = product_model.get_all_products(category)
    # Convert ObjectId to string for JSON serialization
    for product in products:
        product['_id'] = str(product['_id'])
    return jsonify(products), 200

@products_bp.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product_model = current_app.config.get('product_model')
    product = product_model.get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product), 200

@products_bp.route('/products', methods=['POST'])
@login_required
def create_product():
    data = request.get_json()
    
    if not all(k in data for k in ['name', 'description', 'price', 'image_url', 'category']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    product_model = current_app.config.get('product_model')
    product_id = product_model.create_product(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),  # Ensure price is float
        image_url=data['image_url'],
        category=data['category'],
        stock=int(data.get('stock', 0))  # Ensure stock is integer
    )
    
    return jsonify({'message': 'Product created successfully', 'product_id': product_id}), 201

@products_bp.route('/products/<product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No update data provided'}), 400
    
    product_model = current_app.config.get('product_model')
    product = product_model.get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Convert price and stock to proper types if present
    if 'price' in data:
        data['price'] = float(data['price'])
    if 'stock' in data:
        data['stock'] = int(data['stock'])
    
    updated_product = product_model.update_product(product_id, data)
    return jsonify({'message': 'Product updated successfully', 'product': updated_product}), 200

@products_bp.route('/products/<product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    product_model = current_app.config.get('product_model')
    result = product_model.delete_product(product_id)
    if result.deleted_count == 0:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'message': 'Product deleted successfully'}), 200

@products_bp.route('/products/<product_id>/stock', methods=['PUT'])
@login_required
def update_stock(product_id):
    data = request.get_json()
    
    if 'quantity' not in data:
        return jsonify({'error': 'Quantity is required'}), 400
    
    product_model = current_app.config.get('product_model')
    product = product_model.get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    updated_product = product_model.update_stock(product_id, int(data['quantity']))
    return jsonify({'message': 'Stock updated successfully', 'product': updated_product}), 200

@products_bp.route('/products/bulk', methods=['POST'])
@login_required
def create_bulk_products():
    data = request.get_json()
    
    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list of products'}), 400
    
    product_model = current_app.config.get('product_model')
    created_products = []
    errors = []
    
    for idx, product_data in enumerate(data):
        if not all(k in product_data for k in ['name', 'description', 'price', 'image_url', 'category']):
            errors.append({
                'index': idx,
                'error': 'Missing required fields',
                'data': product_data
            })
            continue
        
        try:
            product_id = product_model.create_product(
                name=product_data['name'],
                description=product_data['description'],
                price=float(product_data['price']),
                image_url=product_data['image_url'],
                category=product_data['category'],
                stock=int(product_data.get('stock', 0))
            )
            created_products.append(product_id)
        except Exception as e:
            errors.append({
                'index': idx,
                'error': str(e),
                'data': product_data
            })
    
    response = {
        'message': f'Created {len(created_products)} products successfully',
        'created_products': created_products
    }
    
    if errors:
        response['errors'] = errors
        return jsonify(response), 207  # Multi-Status
    
    return jsonify(response), 201

@products_bp.route('/products/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '')
    if not query:
        return jsonify([]), 200
        
    product_model = current_app.config.get('product_model')
    products = product_model.search_products(query)
    return jsonify(products), 200
