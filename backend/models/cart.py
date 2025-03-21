from bson import ObjectId

class Cart:
    def __init__(self, db):
        self.db = db
        self.collection = db.carts

    def get_cart(self, user_id):
        """Get a user's cart"""
        try:
            print(f'Getting cart for user_id: {user_id}')
            # Convert user_id to string for consistent comparison
            user_id_str = str(user_id)
            cart = self.collection.find_one({'user_id': user_id_str})
            print(f'Found cart: {cart}')
            
            # Return empty list if no cart found
            if not cart or 'items' not in cart:
                print('No cart found or items not in cart')
                return []
                
            # Return the items array
            return cart['items']
        except Exception as e:
            print(f'Database error in get_cart: {str(e)}')
            return []

    def add_item(self, user_id, item_data):
        """Add or update an item in the cart"""
        try:
            print(f'Adding item for user_id: {user_id}')
            print(f'Item data received for adding to cart: {item_data}')
            print(f'Updating cart for user_id: {user_id}')
            
            # Validate input data
            try:
                price = float(item_data.get('price'))
                quantity = int(item_data.get('quantity'))
            except (ValueError, TypeError) as e:
                print(f'Data validation error: {str(e)}')
                return None
            
            # Convert user_id to string for consistent comparison
            user_id_str = str(user_id)
            cart = self.collection.find_one({'user_id': user_id_str})
            print(f'Found existing cart: {cart}')
            
            if not cart:
                cart = {'user_id': user_id_str, 'items': []}
            
            # Check if item already exists
            item_index = next((i for i, item in enumerate(cart['items']) 
                             if item['product_id'] == item_data['product_id']), -1)
            
            if item_index >= 0:
                # Update existing item
                cart['items'][item_index]['quantity'] = quantity
                # Ensure price is stored as float
                cart['items'][item_index]['price'] = price
            else:
                # Add new item
                cart['items'].append({
                    'product_id': item_data['product_id'],
                    'name': item_data['name'],
                    'price': price,  # Already converted to float above
                    'quantity': quantity,  # Already converted to int above
                    'image': item_data.get('image', '')
                })
            
            # Update or insert cart
            result = self.collection.update_one(
                {'user_id': user_id_str},
                {'$set': cart},
                upsert=True
            )
            print(f'Update result: {result}')
            return cart['items']
        except Exception as e:
            print(f'Database error in add_item: {str(e)}')
            return None

    def remove_item(self, user_id, product_id):
        """Remove an item from the cart"""
        try:
            print(f'Removing item for user_id: {user_id}, product_id: {product_id}')
            
            # Convert user_id to string for consistent comparison
            user_id_str = str(user_id)
            
            result = self.collection.update_one(
                {'user_id': user_id_str},
                {'$pull': {'items': {'product_id': product_id}}}
            )
            print(f'Remove item result: {result.modified_count}')
            return result.modified_count > 0
        except Exception as e:
            print(f'Database error in remove_item: {str(e)}')
            return False

    def clear_cart(self, user_id):
        """Clear all items from a user's cart"""
        try:
            print(f'Clearing cart for user_id: {user_id}')
            
            # Convert user_id to string for consistent comparison
            user_id_str = str(user_id)
            
            result = self.collection.delete_one({'user_id': user_id_str})
            print(f'Clear cart result: {result.deleted_count}')
            return result.deleted_count > 0
        except Exception as e:
            print(f'Database error in clear_cart: {str(e)}')
            return False

    def update_item_quantity(self, user_id, product_id, quantity):
        """Update the quantity of an item in the cart"""
        try:
            print(f'Updating quantity for user_id: {user_id}, product_id: {product_id}, quantity: {quantity}')
            
            # Convert user_id to string for consistent comparison
            user_id_str = str(user_id)
            
            if quantity <= 0:
                return self.remove_item(user_id_str, product_id)
            
            result = self.collection.update_one(
                {
                    'user_id': user_id_str,
                    'items.product_id': product_id
                },
                {
                    '$set': {'items.$.quantity': quantity}
                }
            )
            print(f'Update quantity result: {result.modified_count}')
            return result.modified_count > 0
        except Exception as e:
            print(f'Database error in update_item_quantity: {str(e)}')
            return False
