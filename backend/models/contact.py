from datetime import datetime
from bson import ObjectId

class Contact:
    def __init__(self, db):
        self.db = db
        self.collection = db.contacts

    def create_contact(self, name, email, message):
        """Create a new contact form submission"""
        contact_data = {
            'name': name,
            'email': email,
            'message': message,
            'status': 'unread',
            'created_at': datetime.utcnow(),
            'read_at': None
        }
        result = self.collection.insert_one(contact_data)
        return str(result.inserted_id)

    def get_all_contacts(self, status=None):
        """Get all contact form submissions, optionally filtered by status"""
        query = {'status': status} if status else {}
        return list(self.collection.find(query).sort('created_at', -1))

    def get_contact_by_id(self, contact_id):
        """Get a specific contact form submission"""
        return self.collection.find_one({'_id': ObjectId(contact_id)})

    def mark_as_read(self, contact_id):
        """Mark a contact form submission as read"""
        self.collection.update_one(
            {'_id': ObjectId(contact_id)},
            {
                '$set': {
                    'status': 'read',
                    'read_at': datetime.utcnow()
                }
            }
        )
        return self.get_contact_by_id(contact_id)

    def delete_contact(self, contact_id):
        """Delete a contact form submission"""
        return self.collection.delete_one({'_id': ObjectId(contact_id)})
