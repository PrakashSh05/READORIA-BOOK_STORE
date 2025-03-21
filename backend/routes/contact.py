from flask import Blueprint, request, jsonify, current_app
from backend.routes.auth import login_required

contact_bp = Blueprint('contact', __name__, url_prefix='/api')

@contact_bp.route('/contact', methods=['POST'])
def submit_contact():
    """Submit a contact form"""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['name', 'email', 'message']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        contact_model = current_app.config.get('contact_model')
        contact_id = contact_model.create_contact(
            name=data['name'],
            email=data['email'],
            message=data['message']
        )
        
        return jsonify({
            'message': 'Thank you for your message! We will get back to you soon.',
            'contact_id': contact_id
        }), 201
            
    except Exception as e:
        print(f"Error in contact form submission: {e}")
        return jsonify({'error': 'An error occurred while submitting the form.'}), 500

@contact_bp.route('/contact', methods=['GET'])
@login_required
def get_contacts():
    """Get all contact form submissions (admin only)"""
    try:
        contact_model = current_app.config.get('contact_model')
        status = request.args.get('status')
        contacts = contact_model.get_all_contacts(status)
        return jsonify(contacts), 200
    except Exception as e:
        print(f"Error getting contacts: {e}")
        return jsonify({'error': 'An error occurred while fetching contacts.'}), 500

@contact_bp.route('/contact/<contact_id>', methods=['PUT'])
@login_required
def mark_contact_read(contact_id):
    """Mark a contact form submission as read (admin only)"""
    try:
        contact_model = current_app.config.get('contact_model')
        contact = contact_model.mark_as_read(contact_id)
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        return jsonify(contact), 200
    except Exception as e:
        print(f"Error marking contact as read: {e}")
        return jsonify({'error': 'An error occurred while updating contact.'}), 500

@contact_bp.route('/contact/<contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    """Delete a contact form submission (admin only)"""
    try:
        contact_model = current_app.config.get('contact_model')
        result = contact_model.delete_contact(contact_id)
        if result.deleted_count == 0:
            return jsonify({'error': 'Contact not found'}), 404
        return jsonify({'message': 'Contact deleted successfully'}), 200
    except Exception as e:
        print(f"Error deleting contact: {e}")
        return jsonify({'error': 'An error occurred while deleting contact.'}), 500
