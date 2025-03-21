from datetime import datetime
from bson import ObjectId
import re

class Product:
    def __init__(self, db):
        self.db = db
        self.collection = db.products

    def create_product(self, product_data):
        result = self.collection.insert_one(product_data)
        return str(result.inserted_id)

    def get_product_by_id(self, product_id):
        try:
            return self.collection.find_one({'_id': ObjectId(product_id)})
        except Exception as e:
            print(f"Error getting product: {str(e)}")
            return None

    def search_products(self, search_query):
        """
        Search for products by name or description
        
        Args:
            search_query (str): Search query to match against name or description
            
        Returns:
            list: List of matching products
        """
        try:
            # Create a case-insensitive regex pattern
            pattern = re.compile(search_query, re.IGNORECASE)
            
            # Search in both name and description
            products = list(self.collection.find({
                '$or': [
                    {'name': {'$regex': pattern}},
                    {'description': {'$regex': pattern}},
                    {'author': {'$regex': pattern}},  # Also search in author field
                    {'category': {'$regex': pattern}}  # Also search in category field
                ]
            }))
            
            # Convert ObjectId to string for JSON serialization
            for product in products:
                product['_id'] = str(product['_id'])
            
            return products
        except Exception as e:
            print(f"Error searching products: {str(e)}")
            return []

    def get_all_products(self, category=None):
        """Get all products, optionally filtered by category"""
        try:
            query = {'category': category} if category else {}
            products = list(self.collection.find(query))
            
            # Convert ObjectId to string for JSON serialization
            for product in products:
                product['_id'] = str(product['_id'])
            
            return products
        except Exception as e:
            print(f"Error getting products: {str(e)}")
            return []

    def update_product(self, product_id, update_data):
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(product_id)},
                {'$set': update_data}
            )
            if result.modified_count > 0:
                return self.get_product_by_id(product_id)
            return None
        except Exception as e:
            print(f"Error updating product: {str(e)}")
            return None

    def update_stock(self, product_id, quantity):
        self.collection.update_one(
            {'_id': ObjectId(product_id)},
            {'$inc': {'stock': -quantity}}
        )
        return self.get_product_by_id(product_id)

    def delete_product(self, product_id):
        try:
            result = self.collection.delete_one({'_id': ObjectId(product_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting product: {str(e)}")
            return False