// Load user profile data
async function loadProfileData() {
    try {
        // Set default profile picture
        const profilePicElement = document.getElementById('profile-pic');
        profilePicElement.src = 'https://ui-avatars.com/api/?name=User&background=27ae60&color=fff&size=150';
        
        // First try to load basic info from localStorage
        const currentUser = JSON.parse(localStorage.getItem('currentUser')) || {};
        if (currentUser) {
            document.getElementById('profile-name').textContent = currentUser.name || 'User';
            document.getElementById('profile-email').textContent = currentUser.email || '';
            document.getElementById('full-name').value = currentUser.name || '';
            
            // Check if user has a profile pic in localStorage
            if (currentUser.profilePic) {
                profilePicElement.src = currentUser.profilePic;
            } else if (currentUser.name) {
                // Generate avatar based on user's name
                profilePicElement.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(currentUser.name)}&background=27ae60&color=fff&size=150`;
            }
        }
        
        // Then try to fetch complete profile data from API
        const token = localStorage.getItem('token');
        if (!token) {
            customAlert.warning('Please login to view your complete profile');
            return;
        }
        
        const response = await fetch('/api/profile', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Update all profile fields
            document.getElementById('profile-name').textContent = data.name;
            document.getElementById('profile-email').textContent = data.email;
            document.getElementById('full-name').value = data.name;
            document.getElementById('phone').value = data.phone || '';
            document.getElementById('street').value = data.address?.street || '';
            document.getElementById('city').value = data.address?.city || '';
            document.getElementById('state').value = data.address?.state || '';
            document.getElementById('zipcode').value = data.address?.zipcode || '';
            
            // Update profile picture if available
            if (data.profilePic) {
                profilePicElement.src = data.profilePic;
                
                // Update localStorage
                currentUser.profilePic = data.profilePic;
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
            }
        } else {
            const data = await response.json();
            customAlert.error(data.error || 'Failed to load profile data');
        }
    } catch (error) {
        console.error('Error:', error);
        customAlert.error('An error occurred while loading profile data');
    }
}

// Handle profile picture upload
document.getElementById('profile-pic-input').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) {
        customAlert.error('Please upload a valid image file (JPEG, PNG, or GIF)');
        return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        customAlert.error('File size should be less than 5MB');
        return;
    }

    const formData = new FormData();
    formData.append('profilePic', file);

    try {
        const token = localStorage.getItem('token');
        if (!token) {
            customAlert.warning('Please login to update your profile picture');
            return;
        }
        
        // Show loading state
        const profilePicElement = document.getElementById('profile-pic');
        profilePicElement.style.opacity = '0.5';
        
        const response = await fetch('/api/profile/picture', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();
        
        // Reset opacity
        profilePicElement.style.opacity = '1';
        
        if (response.ok) {
            // Update profile picture
            profilePicElement.src = data.profilePicUrl;
            
            // Update localStorage
            const currentUser = JSON.parse(localStorage.getItem('currentUser')) || {};
            currentUser.profilePic = data.profilePicUrl;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            customAlert.success('Profile picture updated successfully');
        } else {
            customAlert.error(data.error || 'Failed to update profile picture');
        }
    } catch (error) {
        console.error('Error:', error);
        customAlert.error('An error occurred while updating profile picture');
        document.getElementById('profile-pic').style.opacity = '1';
    }
});

// Update personal information
async function updatePersonalInfo() {
    const name = document.getElementById('full-name').value.trim();
    const phone = document.getElementById('phone').value.trim();

    if (!name) {
        customAlert.error('Please enter your name');
        return;
    }

    const formData = { name, phone };

    try {
        const token = localStorage.getItem('token');
        if (!token) {
            customAlert.warning('Please login to update your profile');
            return;
        }
        
        const response = await fetch('/api/profile/personal', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        
        if (response.ok) {
            // Update profile display
            document.getElementById('profile-name').textContent = name;
            
            // Update localStorage
            const currentUser = JSON.parse(localStorage.getItem('currentUser')) || {};
            currentUser.name = name;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            customAlert.success('Personal information updated successfully');
        } else {
            customAlert.error(data.error || 'Failed to update personal information');
        }
    } catch (error) {
        console.error('Error:', error);
        customAlert.error('An error occurred while updating personal information');
    }
}

// Update address
async function updateAddress() {
    const street = document.getElementById('street').value.trim();
    const city = document.getElementById('city').value.trim();
    const state = document.getElementById('state').value.trim();
    const zipcode = document.getElementById('zipcode').value.trim();

    if (!street || !city || !state || !zipcode) {
        customAlert.error('Please fill in all address fields');
        return;
    }

    const formData = { street, city, state, zipcode };

    try {
        const token = localStorage.getItem('token');
        if (!token) {
            customAlert.warning('Please login to update your address');
            return;
        }
        
        const response = await fetch('/api/profile/address', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        
        if (response.ok) {
            customAlert.success('Address updated successfully');
        } else {
            customAlert.error(data.error || 'Failed to update address');
        }
    } catch (error) {
        console.error('Error:', error);
        customAlert.error('An error occurred while updating address');
    }
}

// Update password
async function updatePassword() {
    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Validate passwords
    if (!currentPassword || !newPassword || !confirmPassword) {
        customAlert.error('Please fill in all password fields');
        return;
    }

    if (newPassword !== confirmPassword) {
        customAlert.error('New passwords do not match');
        return;
    }

    if (newPassword.length < 6) {
        customAlert.error('Password must be at least 6 characters long');
        return;
    }

    try {
        const token = localStorage.getItem('token');
        if (!token) {
            customAlert.warning('Please login to update your password');
            return;
        }
        
        const response = await fetch('/api/profile/password', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                currentPassword,
                newPassword
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            // Clear password fields
            document.getElementById('current-password').value = '';
            document.getElementById('new-password').value = '';
            document.getElementById('confirm-password').value = '';
            
            customAlert.success('Password updated successfully');
        } else {
            customAlert.error(data.error || 'Failed to update password');
        }
    } catch (error) {
        console.error('Error:', error);
        customAlert.error('An error occurred while updating password');
    }
}

// Delete account
async function confirmDeleteAccount() {
    const confirmed = confirm('Are you sure you want to delete your account? This action cannot be undone.');
    if (!confirmed) return;

    try {
        const token = localStorage.getItem('token');
        if (!token) {
            customAlert.warning('Please login to delete your account');
            return;
        }
        
        const response = await fetch('/api/profile', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        
        if (response.ok) {
            // Clear all user data from localStorage
            localStorage.clear();
            
            customAlert.success('Account deleted successfully. Redirecting to home page...');
            
            // Redirect to home page after a short delay
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            customAlert.error(data.error || 'Failed to delete account');
        }
    } catch (error) {
        console.error('Error:', error);
        customAlert.error('An error occurred while deleting account');
    }
}

// Initialize profile page
document.addEventListener('DOMContentLoaded', function() {
    loadProfileData();
});