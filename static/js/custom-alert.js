class CustomAlert {
    constructor() {
        this.container = null;
        this.timeout = null;
        this.init();
    }

    init() {
        // Create container if it doesn't exist
        if (!document.querySelector('.custom-alert-container')) {
            this.container = document.createElement('div');
            this.container.className = 'custom-alert-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.custom-alert-container');
        }
    }

    show(message, type = 'info', duration = 2000) {
        // Clear any existing timeout
        if (this.timeout) {
            clearTimeout(this.timeout);
        }

        // Create alert element
        const alert = document.createElement('div');
        alert.className = `custom-alert ${type}`;
        
        // Set icon based on type
        let icon = 'info-circle';
        switch(type) {
            case 'success':
                icon = 'check-circle';
                break;
            case 'error':
                icon = 'times-circle';
                break;
            case 'warning':
                icon = 'exclamation-circle';
                break;
        }

        // Create alert content
        alert.innerHTML = `
            <i class="fas fa-${icon} custom-alert-icon"></i>
            <span class="custom-alert-message">${message}</span>
            <i class="fas fa-times custom-alert-close"></i>
        `;

        // Add to container
        this.container.appendChild(alert);

        // Show alert
        setTimeout(() => alert.classList.add('show'), 10);

        // Add close button functionality
        const closeBtn = alert.querySelector('.custom-alert-close');
        closeBtn.addEventListener('click', () => this.hide(alert));

        // Auto hide after duration
        this.timeout = setTimeout(() => this.hide(alert), duration);
    }

    hide(alert) {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }

    // Convenience methods
    success(message, duration) {
        this.show(message, 'success', duration);
    }

    error(message, duration) {
        this.show(message, 'error', duration);
    }

    warning(message, duration) {
        this.show(message, 'warning', duration);
    }

    info(message, duration) {
        this.show(message, 'info', duration);
    }
}

// Create global instance
const customAlert = new CustomAlert(); 