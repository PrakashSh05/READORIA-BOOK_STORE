// Redirect to login page if not logged in
function checkLogin() {
    const currentUser = localStorage.getItem('currentUser'); 
    if (!currentUser) {
        alert('Please login to access the contact page!');
        window.location.href = 'index.html'; // Redirect to login
    }
}

// Handle contact form submission
function handleContactForm(event) {
    event.preventDefault();
    
    const name = document.getElementById('contact-name').value.trim();
    const email = document.getElementById('contact-email').value.trim();
    const message = document.getElementById('contact-message').value.trim();
    
    if (!name || !email || !message) {
        alert('Please fill in all fields.');
        return;
    }

    // Simulate successful submission
    alert('Thank you for your message! We will get back to you soon.');

    // Reset the form after successful submission
    document.querySelector('.contact-form').reset();
}

// Ensure the DOM is fully loaded before executing
window.onload = function() {
    checkLogin(); // Ensure user is logged in

    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactForm);
    }
};