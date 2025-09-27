// Re Studio Booking - Main JavaScript
// Enhanced interactions and functionality

class ReStudioApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupAnimations();
        this.setupFormHandlers();
        this.setupNotifications();
        this.handleRedirection();
        this.setupTheme();
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            // Smooth scrolling for anchor links
            this.setupSmoothScrolling();
            
            // Button loading states
            this.setupButtonLoadingStates();
            
            // Navigation highlighting
            this.setupNavigationHighlight();
            
            // Mobile menu
            this.setupMobileMenu();
            
            // Search functionality
            this.setupSearch();
        });

        // Window events
        window.addEventListener('scroll', () => {
            this.updateNavigationOnScroll();
        });

        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // Update URL without triggering scroll
                    history.pushState(null, null, anchor.getAttribute('href'));
                }
            });
        });
    }

    setupButtonLoadingStates() {
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                // Skip loading for special links
                if (this.href && (
                    this.href.startsWith('#') || 
                    this.href.startsWith('tel:') || 
                    this.href.startsWith('mailto:')
                )) {
                    return;
                }

                // Add loading state
                const originalText = this.innerHTML;
                const originalPointerEvents = this.style.pointerEvents;
                
                this.innerHTML = '<span class="loading"></span> جارٍ التحميل...';
                this.style.pointerEvents = 'none';
                this.setAttribute('data-loading', 'true');
                
                // Restore after timeout or page unload
                const timeout = setTimeout(() => {
                    this.innerHTML = originalText;
                    this.style.pointerEvents = originalPointerEvents;
                    this.removeAttribute('data-loading');
                }, 3000);

                // Clear timeout if page unloads
                window.addEventListener('beforeunload', () => {
                    clearTimeout(timeout);
                });
            });
        });
    }

    setupNavigationHighlight() {
        const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
        const sections = document.querySelectorAll('section[id]');

        if (sections.length === 0) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.getAttribute('id');
                    navLinks.forEach(link => {
                        link.classList.remove('active');
                        if (link.getAttribute('href') === `#${id}`) {
                            link.classList.add('active');
                        }
                    });
                }
            });
        }, {
            threshold: 0.5
        });

        sections.forEach(section => observer.observe(section));
    }

    updateNavigationOnScroll() {
        const nav = document.querySelector('.nav');
        if (nav) {
            if (window.scrollY > 100) {
                nav.style.background = 'rgba(255, 255, 255, 0.95)';
                nav.style.backdropFilter = 'blur(10px)';
            } else {
                nav.style.background = 'var(--white)';
                nav.style.backdropFilter = 'none';
            }
        }
    }

    setupAnimations() {
        // Intersection Observer for animations
        const animateOnScroll = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = entry.target.dataset.animation || 'fadeInUp 0.6s ease-out';
                }
            });
        }, {
            threshold: 0.1
        });

        // Animate cards on scroll
        document.querySelectorAll('.card').forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.dataset.animation = `fadeInUp 0.6s ease-out ${index * 0.1}s forwards`;
            animateOnScroll.observe(card);
        });

        // Add CSS for animations
        if (!document.querySelector('#dynamic-animations')) {
            const style = document.createElement('style');
            style.id = 'dynamic-animations';
            style.textContent = `
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    setupFormHandlers() {
        // Handle booking forms
        const bookingForms = document.querySelectorAll('form[id*="booking"]');
        bookingForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleBookingSubmission(form);
            });
        });

        // Real-time validation
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }

    handleBookingSubmission(form) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading"></span> جارٍ الإرسال...';
            submitBtn.disabled = true;
        }

        // Simulate API call
        fetch(form.action || '/api/method/re_studio_booking.api.create_booking', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'success') {
                this.showNotification('تم إرسال طلب الحجز بنجاح! سنتواصل معك قريباً.', 'success');
                form.reset();
            } else {
                throw new Error(data.exc || 'خطأ في إرسال الطلب');
            }
        })
        .catch(error => {
            console.error('Booking error:', error);
            this.showNotification('حدث خطأ في إرسال الطلب. يرجى المحاولة مرة أخرى.', 'error');
        })
        .finally(() => {
            if (submitBtn) {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Remove previous error styling
        field.classList.remove('error');
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) existingError.remove();

        // Validation rules
        switch (field.type) {
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                isValid = emailRegex.test(value);
                errorMessage = 'يرجى إدخال بريد إلكتروني صحيح';
                break;
            
            case 'tel':
                const phoneRegex = /^[0-9+\-\s()]+$/;
                isValid = phoneRegex.test(value) && value.length >= 10;
                errorMessage = 'يرجى إدخال رقم هاتف صحيح';
                break;
            
            case 'date':
                const selectedDate = new Date(value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                isValid = selectedDate >= today;
                errorMessage = 'يرجى اختيار تاريخ من اليوم أو المستقبل';
                break;
        }

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'هذا الحقل مطلوب';
        }

        if (!isValid) {
            field.classList.add('error');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = errorMessage;
            errorDiv.style.color = 'var(--primary-red)';
            errorDiv.style.fontSize = '0.9em';
            errorDiv.style.marginTop = '5px';
            field.parentNode.appendChild(errorDiv);
        }

        return isValid;
    }

    setupNotifications() {
        // Create notification container if it doesn't exist
        if (!document.querySelector('.notifications-container')) {
            const container = document.createElement('div');
            container.className = 'notifications-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }

        // Check for URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('success') === 'booking') {
            this.showNotification('تم إرسال طلب الحجز بنجاح! سنتواصل معك قريباً.', 'success');
        }
    }

    showNotification(message, type = 'info') {
        const container = document.querySelector('.notifications-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            ${message}
            <button class="close-btn" style="float: left; background: none; border: none; font-size: 1.2em; cursor: pointer;">&times;</button>
        `;
        
        notification.style.cssText = `
            margin-bottom: 10px;
            animation: slideInRight 0.5s ease-out;
        `;

        container.appendChild(notification);

        // Auto remove after 5 seconds
        const timeout = setTimeout(() => {
            this.removeNotification(notification);
        }, 5000);

        // Manual close
        notification.querySelector('.close-btn').addEventListener('click', () => {
            clearTimeout(timeout);
            this.removeNotification(notification);
        });
    }

    removeNotification(notification) {
        notification.style.animation = 'slideOutRight 0.5s ease-out forwards';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    handleRedirection() {
        const redirectTo = document.querySelector('[data-redirect-to]')?.dataset.redirectTo;
        if (redirectTo) {
            let countdown = 3;
            const countdownElement = document.querySelector('.countdown');
            
            if (countdownElement) {
                const interval = setInterval(() => {
                    countdown--;
                    countdownElement.textContent = countdown;
                    
                    if (countdown <= 0) {
                        clearInterval(interval);
                        window.location.href = redirectTo;
                    }
                }, 1000);
            } else {
                setTimeout(() => {
                    window.location.href = redirectTo;
                }, 3000);
            }
        }
    }

    setupMobileMenu() {
        const nav = document.querySelector('.nav');
        if (!nav) return;

        // Create mobile menu button
        const mobileMenuBtn = document.createElement('button');
        mobileMenuBtn.className = 'mobile-menu-btn';
        mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
        mobileMenuBtn.style.cssText = `
            display: none;
            background: none;
            border: none;
            font-size: 1.5em;
            color: var(--primary-red);
            cursor: pointer;
        `;

        const navContent = nav.querySelector('.nav-content');
        const navLinks = nav.querySelector('.nav-links');
        
        navContent.insertBefore(mobileMenuBtn, navLinks);

        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('mobile-open');
        });

        // Add mobile styles
        if (!document.querySelector('#mobile-nav-styles')) {
            const style = document.createElement('style');
            style.id = 'mobile-nav-styles';
            style.textContent = `
                @media (max-width: 768px) {
                    .mobile-menu-btn {
                        display: block !important;
                    }
                    
                    .nav-links {
                        position: absolute;
                        top: 100%;
                        left: 0;
                        right: 0;
                        background: var(--white);
                        flex-direction: column;
                        gap: 10px;
                        padding: 20px;
                        box-shadow: 0 5px 15px var(--shadow);
                        transform: translateY(-100%);
                        opacity: 0;
                        visibility: hidden;
                        transition: all 0.3s ease;
                    }
                    
                    .nav-links.mobile-open {
                        transform: translateY(0);
                        opacity: 1;
                        visibility: visible;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    setupSearch() {
        // Add search functionality for services and photographers
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'البحث في الخدمات والمصورين...';
        searchInput.className = 'search-input';
        searchInput.style.cssText = `
            width: 100%;
            max-width: 400px;
            padding: 12px 20px;
            border: 2px solid var(--light-gray);
            border-radius: 25px;
            font-size: 1em;
            margin: 20px 0;
            transition: var(--transition);
        `;

        // Insert search input before services section
        const servicesSection = document.querySelector('#services');
        if (servicesSection) {
            servicesSection.parentNode.insertBefore(searchInput, servicesSection);
        }

        searchInput.addEventListener('input', (e) => {
            this.performSearch(e.target.value);
        });

        searchInput.addEventListener('focus', () => {
            searchInput.style.borderColor = 'var(--primary-red)';
        });

        searchInput.addEventListener('blur', () => {
            searchInput.style.borderColor = 'var(--light-gray)';
        });
    }

    performSearch(query) {
        const searchTerms = query.toLowerCase().trim();
        
        // Search in services
        const serviceCards = document.querySelectorAll('.service-card');
        serviceCards.forEach(card => {
            const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
            const description = card.querySelector('p')?.textContent.toLowerCase() || '';
            
            if (searchTerms === '' || title.includes(searchTerms) || description.includes(searchTerms)) {
                card.style.display = '';
                card.style.opacity = '1';
            } else {
                card.style.display = 'none';
                card.style.opacity = '0';
            }
        });

        // Search in photographers
        const photographerCards = document.querySelectorAll('.photographer-card');
        photographerCards.forEach(card => {
            const name = card.querySelector('.name')?.textContent.toLowerCase() || '';
            const specialty = card.querySelector('.specialty')?.textContent.toLowerCase() || '';
            const bio = card.querySelector('p')?.textContent.toLowerCase() || '';
            
            if (searchTerms === '' || name.includes(searchTerms) || specialty.includes(searchTerms) || bio.includes(searchTerms)) {
                card.style.display = '';
                card.style.opacity = '1';
            } else {
                card.style.display = 'none';
                card.style.opacity = '0';
            }
        });
    }

    setupTheme() {
        // Detect system theme preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-mode');
        }

        // Listen for theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addListener(e => {
            if (e.matches) {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
        });
    }

    handleResize() {
        // Close mobile menu on resize to desktop
        if (window.innerWidth > 768) {
            const navLinks = document.querySelector('.nav-links');
            if (navLinks) {
                navLinks.classList.remove('mobile-open');
            }
        }
    }

    // Public methods for external access
    static getInstance() {
        if (!window.reStudioApp) {
            window.reStudioApp = new ReStudioApp();
        }
        return window.reStudioApp;
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    ReStudioApp.getInstance();
});

// Add additional CSS animations
const additionalStyles = document.createElement('style');
additionalStyles.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100px); opacity: 0; }
    }
    
    .error {
        border-color: var(--primary-red) !important;
        box-shadow: 0 0 5px rgba(255, 0, 0, 0.3) !important;
    }
`;
document.head.appendChild(additionalStyles);
