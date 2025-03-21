// Initialize cart
let cart = [];
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;

// Fetch cart from backend
async function fetchCart() {
    console.log('Fetching cart...');
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            cart = [];
            displayCart();
            return;
        }

        const response = await fetch('/api/cart', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const cartData = await response.json();
            
            // Validate cart data
            if (Array.isArray(cartData)) {
                cart = cartData.map(item => ({
                    ...item,
                    price: parseFloat(item.price) || 0,
                    quantity: parseInt(item.quantity) || 1
                }));
                console.log('Cart data processed:', cart);
            } else {
                console.error('Invalid cart data format:', cartData);
                cart = [];
            }
            
            displayCart();
        } else {
            console.error('Failed to fetch cart:', response.status);
            cart = [];
            displayCart();
        }
    } catch (error) {
        console.error('Error fetching cart:', error);
        cart = [];
        displayCart();
    }
}

// Add item to cart
async function addToCart(productId, name, price, image = '') {
    console.log('Adding to cart:', { productId, name, price, image });
    
    // Check authentication
    const token = localStorage.getItem('token');
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    
    if (!token || !currentUser) {
        console.log('No token or user found');
        customAlert.warning('Please login to add items to cart!');
        showLoginForm();
        return;
    }

    try {
        // Validate input data
        if (!productId || !name || isNaN(parseFloat(price))) {
            console.error('Invalid product data:', { productId, name, price });
            customAlert.error('Invalid product data');
            return;
        }

        // Make API request
        const response = await fetch('/api/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                product_id: productId,
                name: name,
                price: parseFloat(price),
                quantity: 1,
                image: image || ''
            })
        });

        if (response.ok) {
            await fetchCart();
            customAlert.success('Item added to cart successfully!');
        } else {
            const data = await response.json();
            if (response.status === 401) {
                // Handle authentication errors
                console.log('Authentication failed:', data.error);
                localStorage.removeItem('token');
                localStorage.removeItem('currentUser');
                customAlert.warning('Session expired. Please login again.');
                showLoginForm();
            } else {
                console.error('Cart error:', data.error);
                customAlert.error(data.error || 'Failed to add item to cart');
            }
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        customAlert.error('Failed to add item to cart');
    }
}

// Remove item from cart
async function removeFromCart(productId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/cart?product_id=${productId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            await fetchCart();
            customAlert.success('Item removed from cart');
        } else {
            const data = await response.json();
            customAlert.error(data.error || 'Failed to remove item from cart');
        }
    } catch (error) {
        console.error('Error removing from cart:', error);
        customAlert.error('Failed to remove item from cart');
    }
}

// Update cart item quantity
async function updateCartItemQuantity(productId, quantity) {
    try {
        console.log(`Updating quantity for product ${productId} to ${quantity}`);
        
        // If quantity is 0 or negative, remove the item
        if (quantity <= 0) {
            console.log(`Quantity is ${quantity}, removing item from cart`);
            await removeFromCart(productId);
            return;
        }
        
        const token = localStorage.getItem('token');
        const requestData = {
            product_id: productId,
            quantity: parseInt(quantity)
        };
        
        console.log('Sending request data:', requestData);
        
        const response = await fetch('/api/cart/quantity', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(requestData)
        });

        console.log('Response status:', response.status);
        
        if (response.ok) {
            await fetchCart();
        } else {
            const data = await response.json().catch(e => ({ error: 'Could not parse error response' }));
            console.error('Error response:', data);
            customAlert.error(data.error || 'Failed to update cart');
        }
    } catch (error) {
        console.error('Error updating cart:', error);
        customAlert.error('Failed to update cart');
    }
}

// Display cart items
function displayCart() {
    const cartItemsElement = document.getElementById('cart-items');
    
    // Check if we're on the cart page by looking for cart-specific elements
    const isCartPage = document.getElementById('subtotal') !== null;
    
    // For header cart count (if it exists)
    const cartCountElement = document.getElementById('cart-count');
    
    if (!cartItemsElement) return;
    
    if (cart.length === 0) {
        cartItemsElement.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
        if (cartCountElement) cartCountElement.textContent = '0';
        
        // Update cart page elements if we're on the cart page
        if (isCartPage) {
            document.getElementById('subtotal').textContent = '₹0';
            document.getElementById('total').textContent = '₹40'; // Just delivery charge
        }
        return;
    }
    
    let subtotal = 0;
    cartItemsElement.innerHTML = '';
    
    cart.forEach(item => {
        // Ensure price is a number
        const price = parseFloat(item.price);
        const quantity = parseInt(item.quantity);
        
        if (isNaN(price) || isNaN(quantity)) {
            console.error('Invalid item data:', item);
            return; // Skip this item
        }
        
        const itemTotal = price * quantity;
        subtotal += itemTotal;
        
        const itemElement = document.createElement('div');
        itemElement.className = 'cart-item';
        itemElement.innerHTML = `
            <div class="cart-item-image">
                <img src="${item.image || 'https://via.placeholder.com/80x120?text=Book'}" alt="${item.name}">
            </div>
            <div class="cart-item-details">
                <h4>${item.name}</h4>
                <p class="price">₹${price.toFixed(0)}</p>
                <div class="quantity-controls">
                    <button class="quantity-btn minus" onclick="updateCartItemQuantity('${item.product_id}', ${quantity - 1})">-</button>
                    <span class="quantity">${quantity}</span>
                    <button class="quantity-btn plus" onclick="updateCartItemQuantity('${item.product_id}', ${quantity + 1})">+</button>
                </div>
            </div>
            <div class="cart-item-actions">
                <p class="item-total">₹${itemTotal.toFixed(0)}</p>
                <button class="remove-item" onclick="removeFromCart('${item.product_id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        cartItemsElement.appendChild(itemElement);
    });
    
    // Update cart count in header if element exists
    if (cartCountElement) {
        cartCountElement.textContent = cart.length.toString();
    }
    
    // Update cart page elements if we're on the cart page
    if (isCartPage) {
        // Calculate delivery fee and total
        const deliveryFee = subtotal >= 200 ? 0 : 40;
        const total = subtotal + deliveryFee;
        
        // Update the summary elements
        document.getElementById('subtotal').textContent = `₹${subtotal.toFixed(0)}`;
        document.getElementById('delivery').textContent = `₹${deliveryFee.toFixed(0)}`;
        document.getElementById('total').textContent = `₹${total.toFixed(0)}`;
        
        // Update delivery info message
        const deliveryInfoElement = document.querySelector('.delivery-info span');
        if (deliveryInfoElement) {
            if (subtotal >= 200) {
                deliveryInfoElement.textContent = 'Free delivery applied!';
                deliveryInfoElement.style.color = 'green';
            } else {
                const amountNeeded = (200 - subtotal).toFixed(0);
                deliveryInfoElement.textContent = `Add ₹${amountNeeded} more for free delivery!`;
                deliveryInfoElement.style.color = '';
            }
        }
    }
}

// Initialize cart on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchCart();
    
    // Setup cart toggle
    const cartToggle = document.getElementById('cart-toggle');
    const cartPanel = document.getElementById('cart-panel');
    
    if (cartToggle && cartPanel) {
        cartToggle.addEventListener('click', () => {
            cartPanel.classList.toggle('open');
        });
    }
});
