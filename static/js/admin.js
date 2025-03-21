// Admin configuration
const ADMIN_EMAIL = 'admin@readoria.com';

// Get token from localStorage
function getToken() {
    return localStorage.getItem('token');
}

// Check if user is admin
function isAdmin() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const token = getToken();
    return token && currentUser.isAdmin === true;
}

// Add authorization header to fetch requests
function fetchWithAuth(url, options = {}) {
    options = options || {};
    options.headers = options.headers || {};
    
    const token = getToken();
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return fetch(url, options);
}

// Initialize admin dashboard
async function initAdminDashboard() {
    if (!getToken() || !isAdmin()) {
        window.location.href = '/?error=access_denied';
        return;
    }

    try {
        const response = await fetchWithAuth('/api/admin/verify');
        if (!response.ok) {
            throw new Error('Admin verification failed');
        }

        document.getElementById('admin-content').style.display = 'block';
        await loadDashboardData();
    } catch (error) {
        console.error('Admin initialization error:', error);
        customAlert.error('Failed to initialize admin dashboard');
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        window.location.href = '/?error=init_failed';
    }
}

// Load dashboard data
async function loadDashboardData() {
    try {
        await Promise.all([
            loadProducts(),
            loadOrders(),
            loadStats(),
            loadContacts()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        customAlert.error('Error loading dashboard data');
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetchWithAuth('/api/admin/stats');
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('total-orders').textContent = stats.total_orders;
            document.getElementById('pending-orders').textContent = stats.pending_orders;
            document.getElementById('unread-messages').textContent = stats.unread_messages;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load Products
async function loadProducts() {
    try {
        const response = await fetchWithAuth('/api/admin/products');
        if (!response.ok) throw new Error('Failed to load products');
        
        const products = await response.json();
        const productsList = document.getElementById('products-list');
        if (!productsList) return;
        
        productsList.innerHTML = products.length === 0 ? 
            '<tr><td colspan="5">No products found</td></tr>' :
            products.map(product => `
                <tr>
                    <td>${product.name || 'No name'}</td>
                    <td>${product.category || 'No category'}</td>
                    <td>₹${(product.price || 0).toFixed(0)}</td>
                    <td>${product.stock || 0}</td>
                    <td>
                        <button onclick="editProduct('${product._id}')" class="action-btn edit-btn">Edit</button>
                        <button onclick="deleteProduct('${product._id}')" class="action-btn delete-btn">Delete</button>
                    </td>
                </tr>
            `).join('');
    } catch (error) {
        console.error('Error loading products:', error);
        customAlert.error('Failed to load products');
    }
}

// Load Orders
async function loadOrders() {
    try {
        const response = await fetchWithAuth('/api/admin/orders');
        if (!response.ok) throw new Error('Failed to load orders');
        
        const orders = await response.json();
        const ordersList = document.getElementById('orders-list');
        if (!ordersList) return;
        
        ordersList.innerHTML = orders.length === 0 ?
            '<tr><td colspan="5">No orders found</td></tr>' :
            orders.map(order => {
                // Escape the order data for HTML attribute
                const orderData = encodeURIComponent(JSON.stringify(order));
                
                return `
                <tr>
                    <td class="order-id">${order._id}</td>
                    <td class="order-total">₹${(order.total || 0).toFixed(2)}</td>
                    <td class="order-status">
                        <span class="status-badge status-${order.status || 'pending'}">
                            ${order.status || 'pending'}
                        </span>
                    </td>
                    <td class="order-status-update">
                        <select onchange="updateOrderStatus('${order._id}', this.value)" class="status-select">
                            <option value="pending" ${order.status === 'pending' ? 'selected' : ''}>Pending</option>
                            <option value="processing" ${order.status === 'processing' ? 'selected' : ''}>Processing</option>
                            <option value="shipped" ${order.status === 'shipped' ? 'selected' : ''}>Shipped</option>
                            <option value="delivered" ${order.status === 'delivered' ? 'selected' : ''}>Delivered</option>
                            <option value="cancelled" ${order.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                        </select>
                    </td>
                    <td class="order-actions">
                        <button onclick="viewOrderDetails('${orderData}')" class="btn btn-primary btn-sm">
                            View Details
                        </button>
                    </td>
                </tr>
                `;
            }).join('');
    } catch (error) {
        console.error('Error loading orders:', error);
        customAlert.error('Failed to load orders');
    }
}

// Load Contacts
async function loadContacts() {
    try {
        const response = await fetchWithAuth('/api/admin/contacts');
        if (!response.ok) throw new Error('Failed to load contacts');
        
        const contacts = await response.json();
        const contactsList = document.getElementById('contacts-list');
        if (!contactsList) return;
        
        contactsList.innerHTML = contacts.length === 0 ?
            '<tr><td colspan="6">No messages found</td></tr>' :
            contacts.map(contact => `
                <tr>
                    <td>${contact.name}</td>
                    <td>${contact.email}</td>
                    <td>${contact.message.substring(0, 50)}${contact.message.length > 50 ? '...' : ''}</td>
                    <td>
                        <span class="status-badge ${contact.status === 'unread' ? 'status-unread' : 'status-read'}">
                            ${contact.status}
                        </span>
                    </td>
                    <td>${new Date(contact.created_at).toLocaleString()}</td>
                    <td>
                        <button class="action-btn" onclick="readMessage('${contact._id}')">Read</button>
                        ${contact.status === 'unread' ? `
                            <button class="action-btn" onclick="markContactAsRead('${contact._id}')">Mark as Read</button>
                        ` : ''}
                        <button class="action-btn delete-btn" onclick="deleteContact('${contact._id}')">Delete</button>
                    </td>
                </tr>
            `).join('');
    } catch (error) {
        console.error('Error loading contacts:', error);
        customAlert.error('Failed to load messages');
    }
}

// View order details
function viewOrderDetails(orderData) {
    try {
        const order = JSON.parse(decodeURIComponent(orderData));
        const modal = document.getElementById('order-details-modal');
        const modalContent = document.getElementById('order-details-content');
        
        const items = order.items || [];
        const itemsList = items.map(item => `
            <tr>
                <td>${item.name || 'N/A'}</td>
                <td>${item.quantity || 0}</td>
                <td>₹${(item.price || 0).toFixed(2)}</td>
                <td>₹${((item.price || 0) * (item.quantity || 0)).toFixed(2)}</td>
            </tr>
        `).join('');

        const createdDate = order.created_at ? new Date(order.created_at).toLocaleString() : 'N/A';
        const processedDate = order.processing_date ? new Date(order.processing_date).toLocaleString() : 'N/A';
        const shippedDate = order.shipped_date ? new Date(order.shipped_date).toLocaleString() : 'N/A';
        const deliveredDate = order.delivered_date ? new Date(order.delivered_date).toLocaleString() : 'N/A';

        modalContent.innerHTML = `
            <div class="order-details-section">
                <h3>Order Information</h3>
                <p><strong>Order ID:</strong> ${order._id || 'N/A'}</p>
                <p><strong>Order Date:</strong> ${createdDate}</p>
                <p><strong>Status:</strong> <span class="status-badge status-${order.status || 'pending'}">${order.status || 'pending'}</span></p>
                <p><strong>Total Amount:</strong> ₹${(order.total || 0).toFixed(2)}</p>
            </div>

            <div class="order-details-section">
                <h3>Customer Information</h3>
                <p><strong>Name:</strong> ${order.user_details?.name || 'N/A'}</p>
                <p><strong>Email:</strong> ${order.user_details?.email || 'N/A'}</p>
                <p><strong>Phone:</strong> ${order.user_details?.phone || 'N/A'}</p>
            </div>

            <div class="order-details-section">
                <h3>Shipping Address</h3>
                <p>${order.shipping_address?.street || 'N/A'}</p>
                <p>${order.shipping_address?.city || 'N/A'}, ${order.shipping_address?.state || 'N/A'}</p>
                <p>${order.shipping_address?.zipcode || 'N/A'}</p>
            </div>

            <div class="order-details-section">
                <h3>Order Timeline</h3>
                <div class="timeline">
                    <p><strong>Order Placed:</strong> ${createdDate}</p>
                    <p><strong>Processing Started:</strong> ${processedDate}</p>
                    <p><strong>Shipped:</strong> ${shippedDate}</p>
                    <p><strong>Delivered:</strong> ${deliveredDate}</p>
                </div>
            </div>

            <div class="order-details-section">
                <h3>Order Items</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Quantity</th>
                            <th>Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${itemsList || '<tr><td colspan="4">No items found</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
        
        modal.style.display = 'block';
    } catch (error) {
        console.error('Error displaying order details:', error);
        customAlert.error('Failed to display order details');
    }
}

// Close order details modal
function closeOrderDetailsModal() {
    const modal = document.getElementById('order-details-modal');
    modal.style.display = 'none';
}

// Handle CRUD operations
async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product?')) return;
    try {
        const response = await fetchWithAuth(`/api/admin/products/${productId}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            customAlert.success('Product deleted successfully');
            await loadProducts();
        } else {
            throw new Error('Failed to delete product');
        }
    } catch (error) {
        console.error('Error deleting product:', error);
        customAlert.error(error.message);
    }
}

async function updateOrderStatus(orderId, status) {
    try {
        const response = await fetchWithAuth(`/api/admin/orders/${orderId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        if (response.ok) {
            customAlert.success('Order status updated');
            await loadOrders();
        } else {
            throw new Error('Failed to update order status');
        }
    } catch (error) {
        console.error('Error updating order:', error);
        customAlert.error(error.message);
    }
}

async function readMessage(contactId) {
    try {
        const response = await fetchWithAuth('/api/admin/contacts');
        if (!response.ok) throw new Error('Failed to fetch contacts');
        
        const contacts = await response.json();
        const contact = contacts.find(c => c._id === contactId);
        if (!contact) throw new Error('Message not found');
        
        document.getElementById('message-content').innerHTML = `
            <div class="message-details">
                <p><strong>From:</strong> ${contact.name}</p>
                <p><strong>Email:</strong> ${contact.email}</p>
                <p><strong>Date:</strong> ${new Date(contact.created_at).toLocaleString()}</p>
                <p><strong>Status:</strong> 
                    <span class="status-badge ${contact.status === 'unread' ? 'status-unread' : 'status-read'}">
                        ${contact.status}
                    </span>
                </p>
                <div class="message-body">
                    <h3>Message:</h3>
                    <p>${contact.message}</p>
                </div>
            </div>
        `;
        
        document.getElementById('read-message-modal').classList.add('visible');
        
        if (contact.status === 'unread') {
            await markContactAsRead(contactId);
        }
    } catch (error) {
        console.error('Error reading message:', error);
        customAlert.error(error.message);
    }
}

async function markContactAsRead(contactId) {
    try {
        const response = await fetchWithAuth(`/api/admin/contacts/${contactId}/read`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            await Promise.all([loadContacts(), loadStats()]);
            customAlert.success('Message marked as read');
        } else {
            throw new Error('Failed to mark message as read');
        }
    } catch (error) {
        console.error('Error marking message as read:', error);
        customAlert.error(error.message);
    }
}

async function deleteContact(contactId) {
    if (!confirm('Are you sure you want to delete this message?')) return;
    try {
        const response = await fetchWithAuth(`/api/admin/contacts/${contactId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            customAlert.success('Message deleted successfully');
            await Promise.all([loadContacts(), loadStats()]);
        } else {
            throw new Error('Failed to delete message');
        }
    } catch (error) {
        console.error('Error deleting message:', error);
        customAlert.error(error.message);
    }
}

// Modal handlers
function closeReadMessageModal() {
    document.getElementById('read-message-modal').classList.remove('visible');
}

function showAddProductModal() {
    document.getElementById('add-product-modal').classList.add('visible');
}

function closeAddProductModal() {
    document.getElementById('add-product-modal').classList.remove('visible');
    document.getElementById('add-product-form').reset();
}

function showEditProductModal() {
    document.getElementById('edit-product-modal').classList.add('visible');
}

function closeEditProductModal() {
    document.getElementById('edit-product-modal').classList.remove('visible');
    document.getElementById('edit-product-form').reset();
}

// Initialize image preview functionality
function initImagePreviews() {
    const imageInputs = [
        {
            input: 'product-image',
            preview: 'product-image-preview',
            img: 'product-preview-img'
        },
        {
            input: 'edit-product-image',
            preview: 'edit-product-image-preview',
            img: 'edit-product-preview-img'
        }
    ];
    
    imageInputs.forEach(config => {
        const input = document.getElementById(config.input);
        const preview = document.getElementById(config.preview);
        const previewImg = document.getElementById(config.img);
        
        // Only proceed if we have both input and preview elements
        if (input && preview && previewImg) {
            const placeholder = preview.querySelector('.placeholder');
            preview.addEventListener('click', () => input.click());
            
            input.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewImg.src = e.target.result;
                        previewImg.style.display = 'block';
                        if (placeholder) {
                            placeholder.style.display = 'none';
                        }
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    });
}

// Add new product
async function addProduct(event) {
    event.preventDefault();
    
    try {
        const formData = new FormData();
        formData.append('name', document.getElementById('product-name').value);
        formData.append('description', document.getElementById('product-description').value);
        formData.append('category', document.getElementById('product-category').value);
        formData.append('price', document.getElementById('product-price').value);
        formData.append('stock', document.getElementById('product-stock').value);
        
        const imageFile = document.getElementById('product-image').files[0];
        if (imageFile) {
            formData.append('image', imageFile);
        }

        const response = await fetchWithAuth('/api/admin/products', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Failed to add product');
        
        await loadProducts();
        closeAddProductModal();
        customAlert.success('Product added successfully');
    } catch (error) {
        console.error('Error adding product:', error);
        customAlert.error('Failed to add product');
    }
}

// Update product
async function updateProduct(event) {
    event.preventDefault();
    
    const productId = document.getElementById('edit-product-id').value;
    
    try {
        const formData = new FormData();
        formData.append('name', document.getElementById('edit-product-name').value);
        formData.append('description', document.getElementById('edit-product-description').value);
        formData.append('category', document.getElementById('edit-product-category').value);
        formData.append('price', document.getElementById('edit-product-price').value);
        formData.append('stock', document.getElementById('edit-product-stock').value);
        
        const imageFile = document.getElementById('edit-product-image').files[0];
        if (imageFile) {
            formData.append('image', imageFile);
        }

        const response = await fetchWithAuth(`/api/admin/products/${productId}`, {
            method: 'PUT',
            body: formData
        });

        if (!response.ok) throw new Error('Failed to update product');
        
        await loadProducts();
        closeEditProductModal();
        customAlert.success('Product updated successfully');
    } catch (error) {
        console.error('Error updating product:', error);
        customAlert.error('Failed to update product');
    }
}

// Edit product - Load existing data
async function editProduct(productId) {
    try {
        const response = await fetchWithAuth(`/api/admin/products/${productId}`);
        if (!response.ok) throw new Error('Failed to fetch product');
        
        const product = await response.json();
        
        document.getElementById('edit-product-id').value = product._id;
        document.getElementById('edit-product-name').value = product.name;
        document.getElementById('edit-product-description').value = product.description;
        document.getElementById('edit-product-category').value = product.category;
        document.getElementById('edit-product-price').value = product.price;
        document.getElementById('edit-product-stock').value = product.stock;
        
        // Show existing image in preview
        const previewImg = document.getElementById('edit-product-preview-img');
        const placeholder = document.querySelector('#edit-product-image-preview .placeholder');
        if (previewImg && product.image_url) {
            previewImg.src = product.image_url;
            previewImg.style.display = 'block';
            if (placeholder) {
                placeholder.style.display = 'none';
            }
        } else {
            if (previewImg) previewImg.style.display = 'none';
            if (placeholder) placeholder.style.display = 'block';
        }

        showEditProductModal();
    } catch (error) {
        console.error('Error fetching product:', error);
        customAlert.error('Failed to load product details');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    initAdminDashboard();
    initImagePreviews();
    
    // Add Product Form
    const addProductForm = document.getElementById('add-product-form');
    if (addProductForm) {
        addProductForm.addEventListener('submit', addProduct);
    }
    
    // Edit Product Form
    const editProductForm = document.getElementById('edit-product-form');
    if (editProductForm) {
        editProductForm.addEventListener('submit', updateProduct);
    }
    
    // Modal close buttons
    const closeButtons = document.querySelectorAll('.close');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (button.closest('#add-product-modal')) {
                closeAddProductModal();
            } else if (button.closest('#edit-product-modal')) {
                closeEditProductModal();
            } else if (button.closest('#read-message-modal')) {
                closeReadMessageModal();
            }
        });
    });
    
    // Show Add Product Modal button
    const addProductBtn = document.querySelector('[data-action="show-add-modal"]');
    if (addProductBtn) {
        addProductBtn.addEventListener('click', showAddProductModal);
    }
});