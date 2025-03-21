var searchForm = document.querySelector('.search-form');
var searchBtn = document.querySelector('#search-btn');

if (searchBtn && searchForm) {
    searchBtn.onclick = () => {
        searchForm.classList.toggle('active');
    }
}

window.onscroll = () => {
    if (searchForm) {
        searchForm.classList.remove('active');
    }
    
    // Check if header-2 element exists before trying to access it
    const header2 = document.querySelector('.header .header-2');
    if (header2) {
        if (window.scrollY > 80) {
            header2.classList.add('active');
        } else {
            header2.classList.remove('active');
        }
    }
}

window.onload = () => {
    const header2 = document.querySelector('.header .header-2');
    if (header2) {
        if (window.scrollY > 80) {
            header2.classList.add('active');
        } else {
            header2.classList.remove('active');
        }
    }
    
    // Only call fadeOut if the loader container exists
    const loaderContainer = document.querySelector('.loader-container');
    if (loaderContainer) {
        fadeOut();
    }
}

function loader() {
    const loaderContainer = document.querySelector('.loader-container');
    if (loaderContainer) {
        loaderContainer.classList.add('hidden');
    }
}

function fadeOut() {
    setTimeout(loader, 3000); 
}

// Initialize Swiper sliders only if they exist
const booksSlider = document.querySelector(".books-slider");
if (booksSlider) {
    var swiperBooks = new Swiper(".books-slider", {
        loop: true,
        centeredSlides: true,
        spaceBetween: 30,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false
        },
        breakpoints: {
            0: { 
                slidesPerView: 1,
                spaceBetween: 20
            },
            768: { 
                slidesPerView: 2,
                spaceBetween: 25
            },
            1024: { 
                slidesPerView: 3,
                spaceBetween: 30
            }
        }
    });
}

const featuredSlider = document.querySelector(".featured-slider");
if (featuredSlider) {
    var swiperFeatured = new Swiper(".featured-slider", {
        spaceBetween: 10,
        loop: true,
        centeredSlides: true,
        autoplay: {
            delay: 9500,
            disableOnInteraction: false,
        },
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
        breakpoints: {
            0: {
                slidesPerView: 1,
            },
            450: {
                slidesPerView: 2,
                spaceBetween: 20,
            },
            768: {
                slidesPerView: 3,
                spaceBetween: 25,
            },
            1024: {
                slidesPerView: 4,
                spaceBetween: 30,
            },
        },
    });
}

const arrivalsSlider = document.querySelector(".arrivals-slider");
if (arrivalsSlider) {
    var swiperArrivals = new Swiper(".arrivals-slider", {
        loop: true,
        centeredSlides: true,
        spaceBetween: 20,
        autoplay: {
            delay: 6000,
            disableOnInteraction: false
        },
        breakpoints: {
            0: { slidesPerView: 1 },
            768: { slidesPerView: 2 },
            1024: { slidesPerView: 3 }
        }
    });
}

// Auth Modal Functions
function showLoginForm() {
    const authModal = document.getElementById('auth-modal');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    
    if (!authModal || !loginForm || !signupForm) return;
    
    authModal.style.display = 'block';
    loginForm.classList.add('active');
    signupForm.classList.remove('active');
}

function showSignupForm() {
    const authModal = document.getElementById('auth-modal');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    
    if (!authModal || !loginForm || !signupForm) return;
    
    authModal.style.display = 'block';
    signupForm.classList.add('active');
    loginForm.classList.remove('active');
}

function closeModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function switchForm(type) {
    type === 'login' ? showLoginForm() : showSignupForm();
}

// Check if user is admin
function isAdmin() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const token = localStorage.getItem('token');
    return token && currentUser.isAdmin === true;
}

// Update dashboard visibility
function updateDashboardVisibility() {
    const dashboardLink = document.getElementById('admin-dashboard');
    const dashboardMobileLink = document.getElementById('admin-dashboard-mobile');
    
    if (!dashboardLink || !dashboardMobileLink) return;
    
    if (isAdmin()) {
        dashboardLink.style.display = 'inline-block';
        dashboardMobileLink.style.display = 'inline-block';
    } else {
        dashboardLink.style.display = 'none';
        dashboardMobileLink.style.display = 'none';
    }
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    if (!email || !password) {
        customAlert.warning('Please fill in all fields');
        return;
    }

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Store the JWT token first
            localStorage.setItem('token', data.token);
            
            // Store user info
            const userInfo = {
                email: data.email,
                name: data.name,
                isAdmin: data.is_admin
            };
            localStorage.setItem('currentUser', JSON.stringify(userInfo));
            
            customAlert.success('Login successful!');
            closeModal();
            updateAuthButtons();
            updateDashboardVisibility();
            
            // Show dropdown menu after successful login
            const authContainer = document.querySelector('.auth-container');
            if (authContainer) {
                authContainer.classList.add('logged-in');
            }
            
            if (data.is_admin) {
                window.location.href = `/admin?token=${data.token}`;
            }
        } else {
            throw new Error(data.error || 'Invalid email or password');
        }
    } catch (error) {
        console.error('Login error:', error);
        customAlert.error(error.message || 'Error during login. Please try again.');
    }
}

// Handle Signup
async function handleSignup(event) {
    event.preventDefault();
    const name = document.getElementById('signup-name').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value;
    const confirm = document.getElementById('signup-confirm').value;
    
    if (!name || !email || !password || !confirm) {
        customAlert.warning('Please fill in all fields');
        return;
    }

    if (password !== confirm) {
        customAlert.error('Passwords do not match');
        return;
    }

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            customAlert.success('Account created successfully! Please login with your credentials.');
            showLoginForm();
        } else {
            customAlert.error(data.error || 'Registration failed');
        }
    } catch (error) {
        customAlert.error('Registration failed');
    }
}

// Update auth buttons
function updateAuthButtons() {
    const loginBtn = document.getElementById('login-btn');
    const authContainer = document.querySelector('.auth-container');
    const authDropdown = document.getElementById('auth-dropdown');
    
    if (!loginBtn || !authContainer || !authDropdown) return;

    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    
    // First, remove any existing click handlers to avoid duplicates
    loginBtn.onclick = null;
    
    if (currentUser && currentUser.name) {
        // User is logged in
        loginBtn.innerHTML = `<i class="fas fa-user"></i> ${currentUser.name}`;
        
        // Set click behavior for logged-in state
        loginBtn.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent event bubbling
            authDropdown.style.display = authDropdown.style.display === 'block' ? 'none' : 'block';
        };
        
        authContainer.classList.add('logged-in');
    } else {
        // User is not logged in
        loginBtn.innerHTML = '<i class="fas fa-user-circle"></i>';
        
        // Set click behavior for logged-out state
        loginBtn.onclick = function(e) {
            e.preventDefault();
            showLoginForm();
        };
        
        authContainer.classList.remove('logged-in');
        authDropdown.style.display = 'none'; // Hide dropdown when logged out
    }
}

// Handle Logout
function handleLogout() {
    try {
        // Clear dropdown if it exists
        const authDropdown = document.getElementById('auth-dropdown');
        if (authDropdown) {
            authDropdown.style.display = 'none';
        }
        
        // Remove stored data
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        localStorage.removeItem('cart');
        
        // Reload page
        window.location.reload();
    } catch (error) {
        console.error('Error during logout:', error);
        // Fallback - force reload even if there was an error
        window.location.href = '/';
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize
    updateAuthButtons();
    updateDashboardVisibility();

    // Search functionality
    const searchForm = document.querySelector('#search-form');
    const searchBox = document.querySelector('#search-box');

    if (searchForm && searchBox) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = searchBox.value.trim();
            if (query) {
                window.location.href = `/shop?search=${encodeURIComponent(query)}`;
            }
        });

        // Handle search icon click
        const searchLabel = searchForm.querySelector('label');
        if (searchLabel) {
            searchLabel.addEventListener('click', () => {
                const query = searchBox.value.trim();
                if (query) {
                    window.location.href = `/shop?search=${encodeURIComponent(query)}`;
                }
            });
        }
    }

    // Close modal button
    const closeModalBtn = document.querySelector('[data-action="close-modal"]');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    
    // Handle logout from dropdown menu
    document.querySelectorAll('[data-action="logout"]').forEach(element => {
        element.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const authContainer = document.querySelector('.auth-container');
        const authDropdown = document.getElementById('auth-dropdown');
        
        if (authContainer && authDropdown) {
            // If the click is outside the auth container and the dropdown is visible
            if (!authContainer.contains(e.target) && authDropdown.style.display === 'block') {
                authDropdown.style.display = 'none';
            }
        }
    });

    // Form submissions
    const loginForm = document.querySelector('[data-form="login"]');
    const signupForm = document.querySelector('[data-form="signup"]');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }

    // Form switching
    document.querySelectorAll('[data-action="switch-form"]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            switchForm(e.target.dataset.formType);
        });
    });

    // Close modal on outside click
    window.addEventListener('click', (event) => {
        const modal = document.getElementById('auth-modal');
        if (event.target === modal) closeModal();
    });

    // Scroll handler
    window.addEventListener('scroll', () => {
        const searchForm = document.querySelector('.search-form');
        if (searchForm) {
            searchForm.classList.remove('active');
        }
        
        const header2 = document.querySelector('.header .header-2');
        if (header2) {
            if (window.scrollY > 80) {
                header2.classList.add('active');
            } else {
                header2.classList.remove('active');
            }
        }
    });

    // Loader
    const loaderContainer = document.querySelector('.loader-container');
    if (loaderContainer) {
        function fadeOut() {
            setTimeout(fadeOutLoader, 2000);
        }
        
        function fadeOutLoader() {
            loaderContainer.classList.add('fade-out');
            setTimeout(() => {
                loaderContainer.style.display = 'none';
            }, 300);
        }
        
        fadeOut();
    }

    // Initialize swiper
    const booksSlider = document.querySelector(".books-slider");
    if (booksSlider) {
        var swiperBooks = new Swiper(".books-slider", {
            loop: true,
            centeredSlides: true,
            autoplay: {
                delay: 9500,
                disableOnInteraction: false,
            },
            breakpoints: {
                0: {
                    slidesPerView: 1,
                },
                768: {
                    slidesPerView: 2,
                },
                1024: {
                    slidesPerView: 3,
                },
            },
        });
    }

    // Featured section slider
    const featuredSlider = document.querySelector(".featured-slider");
    if (featuredSlider) {
        var swiperFeatured = new Swiper(".featured-slider", {
            spaceBetween: 10,
            loop: true,
            centeredSlides: true,
            autoplay: {
                delay: 9500,
                disableOnInteraction: false,
            },
            navigation: {
                nextEl: ".swiper-button-next",
                prevEl: ".swiper-button-prev",
            },
            breakpoints: {
                0: {
                    slidesPerView: 1,
                },
                450: {
                    slidesPerView: 2,
                },
                768: {
                    slidesPerView: 3,
                },
                1024: {
                    slidesPerView: 4,
                },
            },
        });
    }

    // Arrivals section slider
    const arrivalsSlider = document.querySelector(".arrivals-slider");
    if (arrivalsSlider) {
        var swiperArrivals = new Swiper(".arrivals-slider", {
            spaceBetween: 10,
            loop: true,
            centeredSlides: true,
            autoplay: {
                delay: 9500,
                disableOnInteraction: false,
            },
            breakpoints: {
                0: {
                    slidesPerView: 1,
                },
                768: {
                    slidesPerView: 2,
                },
                1024: {
                    slidesPerView: 3,
                },
            },
        });
    }

    // Reviews section slider
    const reviewsSlider = document.querySelector(".reviews-slider");
    if (reviewsSlider) {
        var swiperReviews = new Swiper(".reviews-slider", {
            spaceBetween: 10,
            grabCursor: true,
            loop: true,
            centeredSlides: true,
            autoplay: {
                delay: 9500,
                disableOnInteraction: false,
            },
            breakpoints: {
                0: {
                    slidesPerView: 1,
                },
                768: {
                    slidesPerView: 2,
                },
                1024: {
                    slidesPerView: 3,
                },
            },
        });
    }

    // Blogs section slider
    const blogsSlider = document.querySelector(".blogs-slider");
    if (blogsSlider) {
        var swiperBlogs = new Swiper(".blogs-slider", {
            spaceBetween: 10,
            grabCursor: true,
            loop: true,
            centeredSlides: true,
            autoplay: {
                delay: 9500,
                disableOnInteraction: false,
            },
            breakpoints: {
                0: {
                    slidesPerView: 1,
                },
                768: {
                    slidesPerView: 2,
                },
                1024: {
                    slidesPerView: 3,
                },
            },
        });
    }
});
