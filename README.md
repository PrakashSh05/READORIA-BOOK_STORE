# Readoria - Online Bookstore

A modern, feature-rich online bookstore built with Flask and MongoDB. Readoria offers a seamless book shopping experience with secure authentication, real-time cart management, and a beautiful responsive design.

## Features

### User Features
- **User Authentication**
  - Secure login and registration
  - JWT-based authentication
  - Password hashing with bcrypt
  - Profile management

- **Product Catalog**
  - Browse books by category
  - Search functionality
  - Detailed product pages
  - Book recommendations

- **Shopping Cart**
  - Real-time cart updates
  - Quantity management
  - Price calculations
  - Free delivery threshold

- **Checkout Process**
  - Multiple payment options (COD, Online)
  - Address management
  - Order confirmation
  - Custom alerts

### Admin Features
- **Product Management**
  - Add/Edit/Delete products
  - Image upload functionality
  - Stock management
  - Category management

- **Order Management**
  - View all orders
  - Update order status
  - Order history

## Technical Stack

### Backend
- **Framework**: Flask
- **Database**: MongoDB
- **Authentication**: JWT
- **Password Security**: Bcrypt
- **File Upload**: Werkzeug

### Frontend
- **HTML/CSS/JavaScript**
- **Responsive Design**
- **Custom Components**:
  - Alert system
  - Image preview
  - Form validation
  - Cart management

### External Services
- Payment Gateway Integration (Razorpay - Demo Mode)

## Project Structure
```
freshStart/
├── app.py                 # Main application file
├── backend/
│   ├── models/           # Database models
│   │   ├── cart.py
│   │   ├── contact.py
│   │   ├── order.py
│   │   ├── product.py
│   │   └── user.py
│   └── routes/           # API routes
│       ├── admin.py
│       ├── auth.py
│       ├── cart.py
│       ├── contact.py
│       ├── orders.py
│       └── products.py
├── static/
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   ├── images/          # Static images
│   └── uploads/         # User uploads
├── templates/           # HTML templates
│   ├── admin.html
│   ├── cart.html
│   ├── index.html
│   ├── login.html
│   ├── payment.html
│   └── profile.html
└── requirements.txt     # Python dependencies
```

## Features in Detail

### User Authentication
- Secure registration with email verification
- JWT token-based session management
- Password reset functionality
- Profile management with order history

### Product Management
- Rich product details with images
- Category-based organization
- Search and filter options
- Stock tracking

### Shopping Cart
- Real-time updates using JavaScript
- Persistent cart storage
- Quantity validation
- Price calculations with delivery charges

### Checkout System
- Address validation
- Multiple payment options
- Order confirmation emails
- Real-time status updates

### Admin Panel
- Secure admin authentication
- Product CRUD operations
- Image upload with preview
- Order management system

## Security Features
- Password hashing with bcrypt
- JWT authentication
- CORS protection
- Input validation
- File upload validation
- XSS protection

## UI/UX Features
- Responsive design
- Custom alert system
- Loading indicators
- Form validation
- Image previews
- Smooth animations

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd freshStart
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application
```bash
python app.py
```

## Environment Variables
```
MONGO_URI=your_mongodb_uri
JWT_SECRET_KEY=your_jwt_secret
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

## Contact Information
- Location: Bangalore, India
- Email: Readoria@gmail.com
- Phone: +91 123-456-7890

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.