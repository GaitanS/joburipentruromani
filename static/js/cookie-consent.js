/**
 * Cookie Consent Banner
 * Compliant with GDPR, CCPA and other privacy regulations
 */

class CookieConsent {
    constructor() {
        this.consentBanner = null;
        this.consentSaved = this.hasUserConsent();
        this.cookieTypes = {
            necessary: { label: 'Necesare', description: 'Cookies esențiale pentru funcționarea site-ului', required: true },
            functional: { label: 'Funcționale', description: 'Pentru îmbunătățirea experienței, cum ar fi preferințele de limbă' },
            analytics: { label: 'Analitice', description: 'Ne ajută să înțelegem cum este folosit site-ul' },
            advertising: { label: 'Publicitate', description: 'Pentru afișarea de reclame personalizate' },
            thirdParty: { label: 'Terțe părți', description: 'Cookies pentru integrarea cu servicii externe' }
        };
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        if (!this.consentSaved) {
            this.createBanner();
            this.showBanner();
        } else {
            this.applyUserPreferences();
        }
        
        // Add button for users to change preferences later
        this.addPreferencesButton();
    }
    
    createBanner() {
        const banner = document.createElement('div');
        banner.id = 'cookie-consent-banner';
        banner.className = 'cookie-consent fixed-bottom bg-white p-3 shadow-lg';
        banner.style.zIndex = '9999';
        banner.style.borderTop = '1px solid #dee2e6';
        
        let content = `
            <div class="container">
                <div class="row align-items-center mb-3">
                    <div class="col-lg-8">
                        <h5 class="mb-2">Politica de cookies</h5>
                        <p class="mb-0 small">Acest site folosește cookies pentru a vă oferi o experiență personalizată și pentru a ne ajuta să înțelegem cum folosiți site-ul nostru. Puteți alege ce tipuri de cookies acceptați. <a href="/privacy/" class="text-primary">Află mai multe</a> despre cookies și cum le folosim.</p>
                    </div>
                    <div class="col-lg-4 text-lg-end mt-3 mt-lg-0">
                        <button id="cookie-accept-all" class="btn btn-primary me-2">Acceptă toate</button>
                        <button id="cookie-settings" class="btn btn-outline-secondary">Preferințe</button>
                    </div>
                </div>
                <div id="cookie-preferences" class="row" style="display: none;">
                    <div class="col-12">
                        <hr>
                        <h6 class="mb-3">Personalizează preferințele de cookies</h6>
                        <div class="cookie-options mb-3">`;
        
        // Add toggles for each cookie type
        for (const [key, value] of Object.entries(this.cookieTypes)) {
            const isDisabled = value.required ? 'disabled checked' : '';
            content += `
                <div class="form-check mb-2">
                    <input type="checkbox" class="form-check-input" id="cookie-${key}" data-type="${key}" ${isDisabled}>
                    <label class="form-check-label" for="cookie-${key}">
                        <strong>${value.label}</strong> 
                        <span class="small text-muted d-block">${value.description}</span>
                    </label>
                </div>`;
        }
        
        content += `
                        </div>
                        <div class="d-flex justify-content-end">
                            <button id="cookie-save" class="btn btn-primary">Salvează preferințele</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        banner.innerHTML = content;
        this.consentBanner = banner;
        
        // Add event listeners
        setTimeout(() => {
            document.getElementById('cookie-accept-all').addEventListener('click', () => this.acceptAll());
            document.getElementById('cookie-settings').addEventListener('click', () => this.togglePreferences());
            document.getElementById('cookie-save').addEventListener('click', () => this.savePreferences());
        }, 100);
    }
    
    showBanner() {
        if (!this.consentBanner || this.consentSaved) return;
        document.body.appendChild(this.consentBanner);
    }
    
    hideBanner() {
        if (this.consentBanner) {
            this.consentBanner.remove();
        }
    }
    
    togglePreferences() {
        const prefsEl = document.getElementById('cookie-preferences');
        if (prefsEl) {
            prefsEl.style.display = prefsEl.style.display === 'none' ? 'flex' : 'none';
        }
    }
    
    acceptAll() {
        const preferences = {};
        for (const key in this.cookieTypes) {
            preferences[key] = true;
        }
        this.saveUserConsent(preferences);
        this.hideBanner();
        this.applyUserPreferences();
    }
    
    savePreferences() {
        const preferences = {};
        
        // Always set necessary cookies
        preferences.necessary = true;
        
        // Get user selections for other cookie types
        for (const key in this.cookieTypes) {
            if (key === 'necessary') continue; // Already set above
            
            const checkbox = document.getElementById(`cookie-${key}`);
            if (checkbox) {
                preferences[key] = checkbox.checked;
            } else {
                preferences[key] = false;
            }
        }
        
        this.saveUserConsent(preferences);
        this.hideBanner();
        this.applyUserPreferences();
    }
    
    hasUserConsent() {
        return !!localStorage.getItem('cookiePreferences');
    }
    
    saveUserConsent(preferences) {
        localStorage.setItem('cookiePreferences', JSON.stringify({
            preferences,
            timestamp: new Date().toISOString()
        }));
        this.consentSaved = true;
    }
    
    getUserPreferences() {
        const savedPrefs = localStorage.getItem('cookiePreferences');
        if (!savedPrefs) return null;
        
        try {
            return JSON.parse(savedPrefs).preferences;
        } catch (e) {
            console.error('Error parsing saved cookie preferences', e);
            return null;
        }
    }
    
    applyUserPreferences() {
        const prefs = this.getUserPreferences();
        if (!prefs) return;
        
        // Apply AdSense personalization settings
        if (typeof adsbygoogle !== 'undefined') {
            if (!prefs.advertising) {
                // Request non-personalized ads
                adsbygoogle.push({ requestNonPersonalizedAds: 1 });
            } else {
                // Allow personalized ads
                adsbygoogle.push({ requestNonPersonalizedAds: 0 });
            }
        }
        
        // Apply analytics settings (e.g., Google Analytics)
        if (typeof ga !== 'undefined') {
            if (!prefs.analytics) {
                window['ga-disable-UA-XXXXXXXX-X'] = true;
            }
        }
        
        // You can add more cookie management logic here for different categories
    }
    
    addPreferencesButton() {
        // Create a fixed button to access cookie preferences later
        const prefButton = document.createElement('button');
        prefButton.id = 'cookie-preferences-button';
        prefButton.className = 'btn btn-sm btn-light position-fixed';
        prefButton.style.cssText = 'bottom: 20px; left: 20px; z-index: 999; opacity: 0.7;';
        prefButton.innerHTML = '<i class="fas fa-cookie-bite"></i> Cookie Preferences';
        
        prefButton.addEventListener('click', () => {
            if (this.consentBanner && document.body.contains(this.consentBanner)) {
                // Banner is already shown, just toggle preferences
                this.togglePreferences();
            } else {
                // Recreate and show the banner
                this.consentSaved = false;
                this.createBanner();
                this.showBanner();
                this.togglePreferences();
            }
        });
        
        document.body.appendChild(prefButton);
    }
}

// Initialize cookie consent system
const cookieConsent = new CookieConsent();