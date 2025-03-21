from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

class User:
    def __init__(self, db):
        self.db = db
        self.collection = db.users

    def create_user(self, name, email, password, phone=None, address=None):
        user_data = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'phone': phone,
            'address': address,
            'created_at': datetime.utcnow(),
            'is_admin': False
        }
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)

    def get_user_by_email(self, email):
        return self.collection.find_one({'email': email})

    def get_user_by_id(self, user_id):
        return self.collection.find_one({'_id': ObjectId(user_id)})

    def update_user(self, user_id, update_data):
        if 'password' in update_data:
            update_data['password'] = generate_password_hash(update_data['password'])
        
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return self.get_user_by_id(user_id)

    def verify_password(self, user, password):
        return check_password_hash(user['password'], password)

    def delete_user(self, user_id):
        return self.collection.delete_one({'_id': ObjectId(user_id)}) 