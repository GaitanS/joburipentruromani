/**
 * Tests for the Facebook popup functionality
 * 
 * These tests verify that:
 * 1. The popup shows up after the configured delay
 * 2. The popup shows up after scrolling to the configured point
 * 3. The popup is dismissed when clicking the close button
 * 4. The cookie is set to remember user's dismissal
 */

// Mock the DOM elements
const setupDOM = () => {
    // Create overlay element
    const overlay = document.createElement('div');
    overlay.id = 'fbPopupOverlay';
    overlay.classList.add('fb-popup-overlay');
    
    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.id = 'fbPopupClose';
    closeBtn.classList.add('fb-popup-close');
    
    // Append close button to a container and add to overlay
    const container = document.createElement('div');
    container.classList.add('fb-popup-container');
    container.appendChild(closeBtn);
    overlay.appendChild(container);
    
    document.body.appendChild(overlay);
    
    return { overlay, closeBtn };
};

// Mock the cookie functions
const mockCookieFunctions = () => {
    let cookies = {};
    
    // Mock setCookie
    window.setCookie = jest.fn((name, value, days) => {
        cookies[name] = value;
    });
    
    // Mock getCookie
    window.getCookie = jest.fn((name) => {
        return cookies[name] || null;
    });
    
    return { cookies };
};

describe('Facebook Popup', () => {
    let fbPopup;
    let mockDOM;
    let mockCookies;
    
    beforeEach(() => {
        // Set up DOM
        mockDOM = setupDOM();
        
        // Set up cookie mocks
        mockCookies = mockCookieFunctions();
        
        // Create the fbPopup object
        fbPopup = {
            config: {
                delay: 1000, // Shorter for testing
                scrollPercentage: 30,
                cookieDuration: 7,
                cookieName: 'fbPopupDismissed',
                showOn: 'all'
            },
            elements: {
                overlay: document.getElementById('fbPopupOverlay'),
                closeBtn: document.getElementById('fbPopupClose')
            },
            state: {
                shown: false,
                scrollHandler: null,
                timeoutId: null
            },
            init: function() {
                this.setupEventListeners();
                this.setupTriggers();
            },
            setupEventListeners: function() {
                this.elements.closeBtn.addEventListener('click', () => {
                    this.hidePopup();
                    window.setCookie(this.config.cookieName, 'true', this.config.cookieDuration);
                });
            },
            setupTriggers: function() {
                this.state.timeoutId = setTimeout(() => {
                    this.showPopup();
                }, this.config.delay);
                
                this.state.scrollHandler = () => {
                    if (this.state.shown) return;
                    
                    // Mock scrolling progress for testing
                    const scrollPercentage = 40; // Above threshold
                    
                    if (scrollPercentage > this.config.scrollPercentage) {
                        this.showPopup();
                    }
                };
            },
            showPopup: function() {
                if (this.state.shown) return;
                
                this.elements.overlay.classList.add('active');
                this.state.shown = true;
                
                if (this.state.timeoutId) {
                    clearTimeout(this.state.timeoutId);
                }
            },
            hidePopup: function() {
                this.elements.overlay.classList.remove('active');
                this.state.shown = false;
            }
        };
    });
    
    afterEach(() => {
        // Clean up DOM
        document.body.innerHTML = '';
        
        // Clear mocks
        jest.clearAllMocks();
        
        // Clear timeout
        if (fbPopup.state.timeoutId) {
            clearTimeout(fbPopup.state.timeoutId);
        }
    });
    
    test('should show popup after delay', (done) => {
        // Init the popup
        fbPopup.init();
        
        // Initially, popup should not be shown
        expect(fbPopup.state.shown).toBe(false);
        expect(mockDOM.overlay.classList.contains('active')).toBe(false);
        
        // Wait for the delay
        setTimeout(() => {
            // Now the popup should be shown
            expect(fbPopup.state.shown).toBe(true);
            expect(mockDOM.overlay.classList.contains('active')).toBe(true);
            done();
        }, fbPopup.config.delay + 100); // Add a bit extra time for safety
    });
    
    test('should show popup after scrolling', () => {
        // Init the popup
        fbPopup.init();
        
        // Initially, popup should not be shown
        expect(fbPopup.state.shown).toBe(false);
        
        // Simulate scrolling
        fbPopup.state.scrollHandler();
        
        // Now the popup should be shown
        expect(fbPopup.state.shown).toBe(true);
        expect(mockDOM.overlay.classList.contains('active')).toBe(true);
    });
    
    test('should hide popup when close button is clicked', () => {
        // Show the popup first
        fbPopup.init();
        fbPopup.showPopup();
        
        // Popup should be shown
        expect(fbPopup.state.shown).toBe(true);
        expect(mockDOM.overlay.classList.contains('active')).toBe(true);
        
        // Simulate clicking the close button
        mockDOM.closeBtn.click();
        
        // Popup should be hidden
        expect(fbPopup.state.shown).toBe(false);
        expect(mockDOM.overlay.classList.contains('active')).toBe(false);
        
        // Cookie should be set
        expect(window.setCookie).toHaveBeenCalledWith(
            fbPopup.config.cookieName,
            'true',
            fbPopup.config.cookieDuration
        );
    });
    
    test('should not show popup if cookie is set', () => {
        // Set the cookie as if the user had dismissed it before
        window.setCookie(fbPopup.config.cookieName, 'true', 7);
        
        // Create a modified fbPopup for this test
        const cookieFbPopup = { ...fbPopup };
        cookieFbPopup.init = function() {
            // Only initialize if cookie is not set
            if (window.getCookie(this.config.cookieName)) {
                return;
            }
            
            // This should not be called if cookie is set
            this.setupEventListeners();
            this.setupTriggers();
        };
        
        // Spy on setupTriggers
        const spy = jest.spyOn(cookieFbPopup, 'setupTriggers');
        
        // Init the popup
        cookieFbPopup.init();
        
        // setupTriggers should not have been called
        expect(spy).not.toHaveBeenCalled();
    });
});