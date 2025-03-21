from datetime import datetime
from bson import ObjectId

class Order:
    def __init__(self, db):
        self.db = db
        self.collection = db.orders

    def create_order(self, user_id, items, total_amount, shipping_address, payment_method='COD', payment_status='pending'):
        order_data = {
            'user_id': user_id,
            'items': items,
            'total_amount': total_amount,
            'shipping_address': shipping_address,
            'status': 'pending',
            'payment_method': payment_method,
            'payment_status': payment_status,
            'created_at': datetime.utcnow(),
            'processing_date': None,
            'shipped_date': None,
            'delivered_date': None,
            'cancelled_date': None
        }
        result = self.collection.insert_one(order_data)
        return str(result.inserted_id)

    def get_order_by_id(self, order_id):
        """
        Get an order by its ID.
        
        Args:
            order_id (str): The ID of the order to retrieve
            
        Returns:
            dict: Order document if found, None otherwise
        """
        try:
            order_id = ObjectId(order_id)
            order = self.collection.find_one({'_id': order_id})
            if order:
                # Convert ObjectId to string for JSON serialization
                order['_id'] = str(order['_id'])
                if isinstance(order['user_id'], ObjectId):
                    order['user_id'] = str(order['user_id'])
            return order
        except Exception as e:
            print(f"Error getting order by ID: {str(e)}")
            return None

    def get_user_orders(self, user_id):
        # Try to convert string user_id to ObjectId if it's not already
        try:
            if not isinstance(user_id, ObjectId):
                user_id_obj = ObjectId(user_id)
            else:
                user_id_obj = user_id
        except:
            # If conversion fails, use the original user_id
            user_id_obj = user_id
            
        # Find orders with either string or ObjectId user_id
        orders = list(self.collection.find({'user_id': {'$in': [user_id, user_id_obj]}}).sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for order in orders:
            order['_id'] = str(order['_id'])
            if isinstance(order['user_id'], ObjectId):
                order['user_id'] = str(order['user_id'])
                
        return orders

    def get_all_orders(self, status=None):
        """Get all orders, optionally filtered by status"""
        query = {}
        if status:
            query['status'] = status
            
        orders = list(self.collection.find(query).sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for order in orders:
            order['_id'] = str(order['_id'])
            order['user_id'] = str(order['user_id'])
            
        return orders

    def update_order_status(self, order_id, update_data):
        """
        Update the status of an order.
        
        Args:
            order_id (str): The ID of the order to update
            update_data (dict): Dictionary containing status and date updates
            
        Returns:
            dict: Updated order document
        """
        try:
            order_id = ObjectId(order_id)
            result = self.collection.update_one(
                {'_id': order_id},
                {'$set': update_data}
            )
            
            if result.modified_count == 0:
                raise ValueError('Order not found or no changes made')
                
            updated_order = self.collection.find_one({'_id': order_id})
            if not updated_order:
                raise ValueError('Failed to retrieve updated order')
                
            return updated_order
            
        except Exception as e:
            print(f"Error updating order status: {str(e)}")
            raise

    def update_payment_status(self, order_id, payment_status):
        """Update the payment status of an order"""
        self.collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'payment_status': payment_status}}
        )
        return self.get_order_by_id(order_id)

    def delete_order(self, order_id):
        return self.collection.delete_one({'_id': ObjectId(order_id)}) 