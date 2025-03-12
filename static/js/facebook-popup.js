/**
 * Facebook Popup Module
 * Shows a Facebook like/follow popup after a specified delay or scroll percentage
 * Remembers when a user dismisses it to avoid showing it repeatedly
 */
document.addEventListener('DOMContentLoaded', function() {
    const fbPopup = {
        // Configuration
        config: {
            // Show popup after this many milliseconds (default: 20 seconds)
            delay: 20000,
            // Show popup when user has scrolled this percentage (default: 30%)
            scrollPercentage: 30,
            // Days to remember the user dismissed the popup (default: 7 days)
            cookieDuration: 7,
            // Cookie name 
            cookieName: 'fbPopupDismissed',
            // Show popup on all pages or just the home page ('all' or 'home')
            showOn: 'all'
        },
        
        // DOM elements
        elements: {
            overlay: document.getElementById('fbPopupOverlay'),
            closeBtn: document.getElementById('fbPopupClose')
        },
        
        // State
        state: {
            shown: false,
            scrollHandler: null,
            timeoutId: null
        },
        
        /**
         * Initialize the Facebook popup
         */
        init: function() {
            // Exit if elements aren't found
            if (!this.elements.overlay || !this.elements.closeBtn) {
                return;
            }
            
            // Check if we should show popup based on page
            if (this.config.showOn === 'home' && window.location.pathname !== '/' && window.location.pathname !== '/index.html') {
                return;
            }
            
            // Check if user has dismissed popup recently
            if (this.getCookie(this.config.cookieName)) {
                return;
            }
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Set up triggers based on time and scroll
            this.setupTriggers();
        },
        
        /**
         * Set up event listeners for the popup
         */
        setupEventListeners: function() {
            // Close button click handler
            this.elements.closeBtn.addEventListener('click', () => {
                this.hidePopup();
                this.setCookie(this.config.cookieName, 'true', this.config.cookieDuration);
            });
            
            // Close on overlay click (outside the popup container)
            this.elements.overlay.addEventListener('click', (e) => {
                if (e.target === this.elements.overlay) {
                    this.hidePopup();
                    this.setCookie(this.config.cookieName, 'true', this.config.cookieDuration);
                }
            });
            
            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.state.shown) {
                    this.hidePopup();
                    this.setCookie(this.config.cookieName, 'true', this.config.cookieDuration);
                }
            });
        },
        
        /**
         * Set up triggers for showing the popup
         */
        setupTriggers: function() {
            // Time-based trigger
            this.state.timeoutId = setTimeout(() => {
                this.showPopup();
            }, this.config.delay);
            
            // Scroll-based trigger
            this.state.scrollHandler = () => {
                if (this.state.shown) return;
                
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                const totalHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                const scrolledPercentage = (scrollTop / totalHeight) * 100;
                
                if (scrolledPercentage > this.config.scrollPercentage) {
                    this.showPopup();
                    // Remove scroll listener after showing
                    window.removeEventListener('scroll', this.state.scrollHandler);
                }
            };
            
            window.addEventListener('scroll', this.state.scrollHandler);
        },
        
        /**
         * Show the popup
         */
        showPopup: function() {
            if (this.state.shown) return;
            
            this.elements.overlay.classList.add('active');
            this.state.shown = true;
            
            // Clear timeout if popup was shown by scroll
            if (this.state.timeoutId) {
                clearTimeout(this.state.timeoutId);
            }
        },
        
        /**
         * Hide the popup
         */
        hidePopup: function() {
            this.elements.overlay.classList.remove('active');
            this.state.shown = false;
        },
        
        /**
         * Set a cookie
         */
        setCookie: function(name, value, days) {
            let expires = '';
            if (days) {
                const date = new Date();
                date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                expires = '; expires=' + date.toUTCString();
            }
            document.cookie = name + '=' + (value || '') + expires + '; path=/';
        },
        
        /**
         * Get a cookie value
         */
        getCookie: function(name) {
            const nameEQ = name + '=';
            const ca = document.cookie.split(';');
            for (let i = 0; i < ca.length; i++) {
                let c = ca[i];
                while (c.charAt(0) === ' ') c = c.substring(1, c.length);
                if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
            }
            return null;
        }
    };
    
    // Initialize the Facebook popup
    fbPopup.init();
});