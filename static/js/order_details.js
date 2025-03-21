// Function to format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(amount);
}

// Function to get status class
function getStatusClass(status) {
    const statusMap = {
        'pending': 'status-pending',
        'processing': 'status-processing',
        'shipped': 'status-shipped',
        'delivered': 'status-delivered',
        'cancelled': 'status-cancelled'
    };
    return statusMap[status.toLowerCase()] || 'status-pending';
}

// Function to update timeline status
function updateTimelineStatus(order) {
    const timelineItems = {
        'ordered': document.getElementById('timeline-ordered'),
        'processing': document.getElementById('timeline-processing'),
        'shipped': document.getElementById('timeline-shipped'),
        'delivered': document.getElementById('timeline-delivered')
    };

    // Reset all items
    Object.values(timelineItems).forEach(item => {
        item.classList.remove('active', 'completed');
    });

    // Set status based on order status
    switch (order.status.toLowerCase()) {
        case 'delivered':
            timelineItems.delivered.classList.add('completed');
            timelineItems.shipped.classList.add('completed');
            timelineItems.processing.classList.add('completed');
            timelineItems.ordered.classList.add('completed');
            break;
        case 'shipped':
            timelineItems.shipped.classList.add('active');
            timelineItems.processing.classList.add('completed');
            timelineItems.ordered.classList.add('completed');
            break;
        case 'processing':
            timelineItems.processing.classList.add('active');
            timelineItems.ordered.classList.add('completed');
            break;
        case 'pending':
            timelineItems.ordered.classList.add('active');
            break;
        case 'cancelled':
            // For cancelled orders, show only the ordered status
            timelineItems.ordered.classList.add('completed');
            break;
    }
}

// Function to create order item HTML
function createOrderItemHTML(item) {
    return `
        <div class="order-item">
            <img src="${item.image}" alt="${item.name}" class="item-image">
            <div class="item-details">
                <div class="item-name">${item.name}</div>
                <div class="item-price">${formatCurrency(item.price)}</div>
                <div class="item-quantity">Quantity: ${item.quantity}</div>
            </div>
        </div>
    `;
}

// Function to create order card HTML
function createOrderCard(order) {
    // Generate HTML for order items
    const orderItemsHTML = order.items && order.items.length > 0 
        ? `
            <div class="order-items-container">
                <h4>Items Ordered:</h4>
                <div class="order-items">
                    ${order.items.map(item => createOrderItemHTML(item)).join('')}
                </div>
            </div>
        ` 
        : '<div class="no-items">No items information available</div>';

    return `
        <div class="order-card">
            <div class="order-header">
                <div class="order-info">
                    <h3>Order #${order._id}</h3>
                    <p class="order-date">${formatDate(order.created_at)}</p>
                </div>
                <div class="order-status ${getStatusClass(order.status)}">
                    ${order.status}
                </div>
            </div>
            
            ${orderItemsHTML}
            
            <div class="order-total">
                <span>Total Amount:</span>
                <span>${formatCurrency(order.total_amount)}</span>
            </div>
        </div>
    `;
}

// Function to load orders
async function loadOrders() {
    const ordersList = document.getElementById('orders-list');
    const emptyState = document.getElementById('empty-state');
    
    try {
        // Get token from localStorage
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('No token found in localStorage');
            // Redirect to login page with error message
            window.location.href = '/?error=login_required';
            return;
        }

        console.log('Attempting to fetch orders with token');
        
        // Fetch orders with authentication
        const response = await fetch('/api/orders', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        console.log('Response status:', response.status);
        
        // Handle different response statuses
        if (response.status === 401) {
            console.error('Authentication failed - Token expired or invalid');
            // Clear auth data and redirect to login
            localStorage.removeItem('token');
            localStorage.removeItem('currentUser');
            window.location.href = '/?error=session_expired';
            return;
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error response:', errorData);
            throw new Error(errorData.error || 'Failed to fetch orders');
        }

        // Parse response data
        const orders = await response.json();
        console.log('Orders received:', orders);
        
        // Display orders or empty state
        if (!orders || orders.length === 0) {
            console.log('No orders found');
            ordersList.style.display = 'none';
            emptyState.style.display = 'flex';
            return;
        }

        // Render orders
        console.log(`Displaying ${orders.length} orders`);
        ordersList.style.display = 'block';
        emptyState.style.display = 'none';
        
        // Generate HTML for each order
        ordersList.innerHTML = '';
        orders.forEach(order => {
            const orderCard = document.createElement('div');
            orderCard.innerHTML = createOrderCard(order);
            ordersList.appendChild(orderCard.firstElementChild);
        });

    } catch (error) {
        console.error('Error loading orders:', error);
        // Show error message
        ordersList.style.display = 'none';
        emptyState.style.display = 'flex';
        emptyState.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-circle"></i>
                <h3>Error Loading Orders</h3>
                <p>${error.message || 'Failed to load orders. Please try again later.'}</p>
                <button onclick="location.reload()" class="btn">Try Again</button>
            </div>
        `;
    }
}

// Function to show alert
function showAlert(message, type = 'success') {
    customAlert[type](message);
}

// Load orders when the page loads
document.addEventListener('DOMContentLoaded', loadOrders);