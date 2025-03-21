from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import os
from werkzeug.utils import secure_filename
from ..routes.auth import login_required

profile_bp = Blueprint('profile', __name__)

UPLOAD_FOLDER = 'static/uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    try:
        # Get user model from current app
        user_model = current_app.config.get('user_model')
        current_user = user_model.get_user_by_id(request.user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        # Convert ObjectId to string for JSON serialization
        user_data = {
            'id': str(current_user['_id']),
            'name': current_user.get('name', ''),
            'email': current_user.get('email', ''),
            'phone': current_user.get('phone', ''),
            'address': current_user.get('address', {}),
            'profilePic': current_user.get('profilePic', '')
        }
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/api/profile/personal', methods=['PUT'])
@login_required
def update_personal_info():
    try:
        data = request.get_json()
        
        # Get user model from current app
        user_model = current_app.config.get('user_model')
        
        update_data = {
            'name': data.get('name'),
            'phone': data.get('phone')
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if not update_data:
            return jsonify({'error': 'No data to update'}), 400
            
        updated_user = user_model.update_user(request.user_id, update_data)
        
        if updated_user:
            return jsonify({'message': 'Personal information updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update user'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/api/profile/address', methods=['PUT'])
@login_required
def update_address():
    try:
        data = request.get_json()
        
        # Get user model from current app
        user_model = current_app.config.get('user_model')
        
        address_data = {
            'address': {
                'street': data.get('street', ''),
                'city': data.get('city', ''),
                'state': data.get('state', ''),
                'zipcode': data.get('zipcode', '')
            }
        }
        
        updated_user = user_model.update_user(request.user_id, address_data)
        
        if updated_user:
            return jsonify({'message': 'Address updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update address'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/api/profile/password', methods=['PUT'])
@login_required
def update_password():
    try:
        data = request.get_json()
        
        # Get user model from current app
        user_model = current_app.config.get('user_model')
        current_user = user_model.get_user_by_id(request.user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        # Verify current password
        if not user_model.verify_password(current_user, data['currentPassword']):
            return jsonify({'error': 'Current password is incorrect'}), 400
            
        # Update password - don't hash here, let the model do it
        update_data = {'password': data['newPassword']}
        updated_user = user_model.update_user(request.user_id, update_data)
        
        if updated_user:
            return jsonify({'message': 'Password updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update password'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/api/profile/picture', methods=['POST'])
@login_required
def update_profile_picture():
    try:
        if 'profilePic' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['profilePic']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if file and allowed_file(file.filename):
            # Create upload folder if it doesn't exist
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Get user model from current app
            user_model = current_app.config.get('user_model')
            
            # Secure filename and save file
            filename = secure_filename(f"{request.user_id}_{file.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Update user profile picture URL in database
            profile_pic_url = f'/{filepath}'
            updated_user = user_model.update_user(request.user_id, {'profilePic': profile_pic_url})
            
            if updated_user:
                return jsonify({
                    'message': 'Profile picture updated successfully',
                    'profilePicUrl': profile_pic_url
                }), 200
            else:
                # Remove uploaded file if database update fails
                try:
                    os.remove(filepath)
                except:
                    pass
                return jsonify({'error': 'Failed to update profile picture'}), 400
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile_bp.route('/api/profile', methods=['DELETE'])
@login_required
def delete_account():
    try:
        # Get user model from current app
        user_model = current_app.config.get('user_model')
        current_user = user_model.get_user_by_id(request.user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
            
        # Delete user's profile picture if exists
        profile_pic = current_user.get('profilePic', '')
        if profile_pic:
            try:
                pic_path = profile_pic.lstrip('/')
                if os.path.exists(pic_path):
                    os.remove(pic_path)
            except Exception as e:
                print(f"Error deleting profile picture: {e}")
        
        # Delete user
        result = user_model.delete_user(request.user_id)
        
        if result.deleted_count > 0:
            return jsonify({'message': 'Account deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete account'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
