/**
 * main.js - Core JavaScript functionality for JoburiPentruRomani
 * Handles responsive behavior, accessibility improvements, and general UX enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile optimization
    initMobileOptimizations();
    
    // Ensure responsive images and ads
    makeImagesResponsive();
    
    // Improve navbar behavior
    enhanceNavbar();

    // Enhance offcanvas mobile menu
    enhanceOffcanvasMenu();
    
    // Initialize bootstrap components
    initBootstrapComponents();
    
    // Add accessibility improvements
    enhanceAccessibility();
});

/**
 * Mobile optimizations
 */
function initMobileOptimizations() {
    // Fix viewport issues on mobile - prevent unintended zooming on input focus
    const viewportMeta = document.querySelector('meta[name="viewport"]');
    if (viewportMeta && /iPhone|iPad|iPod/.test(navigator.userAgent)) {
        viewportMeta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0';
        
        // Add event listeners to restore scalability after input blur
        document.addEventListener('touchend', function(event) {
            if (event.target.tagName !== 'INPUT' && event.target.tagName !== 'TEXTAREA') {
                viewportMeta.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0';
            }
        });
    }
    
    // Collapse navbar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        const navbar = document.getElementById('navbarNav');
        if (navbar && navbar.classList.contains('show')) {
            const isNavbarToggler = event.target.closest('.navbar-toggler');
            const isNavbarMenu = event.target.closest('.navbar-collapse');
            
            // We now use offcanvas instead of collapse, so this is handled differently
        }
    });
    
    // Fix double tap issue on iOS
    if (/iPhone|iPad|iPod/.test(navigator.userAgent)) {
        const links = document.querySelectorAll('a');
        links.forEach(function(link) {
            link.addEventListener('touchend', function(e) {
                // Prevent default if link has no href or # href
                if (!this.getAttribute('href') || this.getAttribute('href') === '#') {
                    e.preventDefault();
                }
            });
        });
    }
}

/**
 * Make images responsive
 */
function makeImagesResponsive() {
    // Make all images responsive
    const images = document.querySelectorAll('img:not(.img-fluid)');
    images.forEach(function(img) {
        img.classList.add('img-fluid');
    });
    
    // Ensure AdSense is responsive
    const adContainers = document.querySelectorAll('.ad-container');
    adContainers.forEach(function(container) {
        // Add resize event listener to handle responsive ads
        window.addEventListener('resize', function() {
            // Force redraw of ad container on resize
            container.style.display = 'none';
            setTimeout(() => { container.style.display = 'block'; }, 50);
        });
    });
}

/**
 * Enhance navbar behavior
 */
function enhanceNavbar() {
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        const dropdowns = document.querySelectorAll('.dropdown-menu.show');
        if (dropdowns.length > 0) {
            const isDropdownToggle = event.target.classList.contains('dropdown-toggle');
            const isInDropdown = event.target.closest('.dropdown-menu');
            
            if (!isDropdownToggle && !isInDropdown) {
                dropdowns.forEach(function(dropdown) {
                    dropdown.classList.remove('show');
                });
            }
        }
    });
    
    // Make navbar sticky on scroll
    let lastScrollTop = 0;
    const header = document.querySelector('header');
    
    if (header) {
        window.addEventListener('scroll', function() {
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // Add shadow when scrolled
            if (scrollTop > 10) {
                header.classList.add('shadow-sm');
            } else {
                header.classList.remove('shadow-sm');
            }
            
            lastScrollTop = scrollTop;
        });
    }
}

/**
 * Enhance the offcanvas mobile menu behavior
 */
function enhanceOffcanvasMenu() {
    const offcanvasElement = document.getElementById('navbarOffcanvas');
    
    if (offcanvasElement) {
        // Create slide in animation effect
        offcanvasElement.addEventListener('show.bs.offcanvas', function () {
            // Add shadow to left edge as the menu slides in
            this.style.boxShadow = '-5px 0 15px rgba(0, 0, 0, 0.1)';
            
            // Animate menu items with a slight delay for each
            const menuItems = this.querySelectorAll('.nav-link, .btn');
            menuItems.forEach(function(item, index) {
                item.style.opacity = '0';
                item.style.transform = 'translateX(20px)';
                item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                
                // Staggered animation for menu items
                setTimeout(function() {
                    item.style.opacity = '1';
                    item.style.transform = 'translateX(0)';
                }, 100 + (index * 50));
            });
        });
        
        // Close the offcanvas menu when clicking menu items that link to pages
        const offcanvasLinks = offcanvasElement.querySelectorAll('a[href]:not([href="#"])');
        offcanvasLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                // Close the offcanvas
                const offcanvasInstance = bootstrap.Offcanvas.getInstance(offcanvasElement);
                if (offcanvasInstance) {
                    offcanvasInstance.hide();
                }
            });
        });
    }
    
    // Ensure the offcanvas is properly hidden when view resizes to desktop
    window.addEventListener('resize', debounce(handleOffcanvasOnResize, 150));
}

/**
 * Initialize Bootstrap components
 */
function initBootstrapComponents() {
    // Initialize all tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(function(tooltip) {
        new bootstrap.Tooltip(tooltip);
    });
    
    // Initialize all popovers
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(function(popover) {
        new bootstrap.Popover(popover);
    });
    
    // Initialize all toasts
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(function(toast) {
        new bootstrap.Toast(toast);
    });
}

/**
 * Enhance accessibility
 */
function enhanceAccessibility() {
    // Add missing aria labels
    const unlabeledButtons = document.querySelectorAll('button:not([aria-label]):not([aria-labelledby])');
    unlabeledButtons.forEach(function(button) {
        if (button.textContent.trim() === '' && !button.getAttribute('aria-label')) {
            // Attempt to infer a label from icon classes
            if (button.querySelector('.fa-search')) {
                button.setAttribute('aria-label', 'Search');
            } else if (button.querySelector('.fa-times')) {
                button.setAttribute('aria-label', 'Close');
            } else if (button.querySelector('.fa-bars')) {
                button.setAttribute('aria-label', 'Menu');
            }
        }
    });
    
    // Ensure proper contrast
    document.querySelectorAll('.text-muted').forEach(function(element) {
        element.style.color = '#6c757d !important'; // Ensuring WCAG AA compliance
    });
    
    // Add keyboard navigation for custom components
    document.querySelectorAll('.category-card').forEach(function(card, index) {
        card.setAttribute('tabindex', '0');
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const link = card.querySelector('a');
                if (link) link.click();
            }
        });
    });
}

/**
 * Handle offcanvas menu when resizing to desktop
 */
function handleOffcanvasOnResize() {
    if (window.innerWidth >= 992) { // Bootstrap lg breakpoint
        const offcanvasElement = document.getElementById('navbarOffcanvas');
        if (offcanvasElement) {
            const offcanvasInstance = bootstrap.Offcanvas.getInstance(offcanvasElement);
            if (offcanvasInstance) offcanvasInstance.hide();
        }
    }
}

/**
 * Debounce function to limit function calls
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}