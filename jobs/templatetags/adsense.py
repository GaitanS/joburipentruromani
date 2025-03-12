from django import template
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.conf import settings
from jobs.models import AdPlacement

register = template.Library()

@register.simple_tag(takes_context=True)
def render_ad(context, position):
    """
    Randează o reclamă pentru poziția specificată dacă există și este activă.
    Utilizare: {% render_ad 'header' %}
    """
    try:
        request = context.get('request')
        
        # Dacă nu există request în context, returnăm string gol
        if not request:
            return ''
        
        # Detecție simplă a dispozitivului (poate fi îmbunătățită)
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        # Enhanced device detection
        if 'mobi' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            device = 'mobile'
        elif 'ipad' in user_agent or 'tablet' in user_agent:
            device = 'tablet'
        else:
            device = 'desktop'
        
        # Find ads for this position - either for all devices or for the current device
        ads = AdPlacement.objects.filter(
            position=position, 
            is_active=True
        ).filter(
            Q(target_devices='all') | Q(target_devices=device)
        )

        # Don't show ads if user is staff (to prevent accidental clicks)
        if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
            return ''
            
        # Check if we're in debug mode and show placeholder if true
        if getattr(settings, 'DEBUG', False):
            return mark_safe(
                f'<div class="ad-debug-placeholder p-3 border border-warning bg-light text-center">'
                f'<small>AdSense Placeholder: {position} ({device})</small></div>'
            )
            
        ad = ads.first()
        if ad:
            # Adaugă comentarii HTML pentru a identifica ușor poziția reclamei în pagină
            return mark_safe(f'<!-- AdSense: {ad.position} start -->\n{ad.ad_code}\n<!-- AdSense: {ad.position} end -->')
    except Exception as e:
        # Log error silently, don't break the page
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error rendering ad at position {position}: {str(e)}")
    
    return ''


@register.simple_tag(takes_context=True)
def render_native_ad_job(context, max_count=1, premium=False):
    """
    Randează un job sponsorizat ca reclamă nativă.
    Utilizare: {% render_native_ad_job %}
    
    Parameters:
    -----------
    max_count: Maximum number of native ads to render
    premium: If True, renders a premium-styled native ad
    context: Template context (automatically provided)
    """
    try:
        # În implementarea reală, aici am putea avea logică pentru a alege un job 
        # sponsorizat pentru a fi afișat ca reclamă nativă
        ad_html = '''
        <div class="job-card sponsored">
            <span class="sponsored-tag">Sponsorizat</span>
            <h5 class="card-title mb-2">Titlu Job Sponsorizat</h5>
            <p class="company-name mb-1">Companie Sponsor</p>
            <p class="location text-muted mb-2">
                <i class="fas fa-map-marker-alt me-1"></i> București, România
                <span class="badge bg-success ms-2">Remote</span>
            </p>
            <div class="d-flex justify-content-between align-items-center mt-3">
                <span class="salary text-success fw-bold">3,500 - 5,000 RON/lună</span>
                <a href="#" class="btn btn-outline-primary btn-sm">Vezi detalii</a>
            </div>
        </div>
        '''
        
        # Enhanced premium ad styling
        if premium:
            premium_ad_html = '''
            <div class="job-card sponsored premium border-warning">
                <div class="ribbon ribbon-top-right"><span>Premium</span></div>
                <span class="sponsored-tag bg-warning text-dark">Job Premium</span>
                <h5 class="card-title mb-2">Poziție Premium Sponsorizată</h5>
                <p class="company-name mb-1">Companie Parteneră</p>
                <p class="mb-3 small">Oportunitate excelentă de angajare cu beneficii complete și pachet salarial competitiv.</p>
                <p class="location text-muted mb-2">
                    <i class="fas fa-map-marker-alt me-1"></i> București, România
                </p>
                <a href="#" class="btn btn-warning btn-sm w-100 mt-2">Aplică Acum</a>
            </div>
            '''
            return mark_safe(premium_ad_html)
            
        return mark_safe(ad_html)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error rendering native ad job: {str(e)}")
        return ''


@register.filter
def inject_ad_every(jobs, n):
    """
    Filter pentru a injecta reclame în listele de joburi la fiecare n elemente.
    Utilizare: {% for job in jobs|inject_ad_every:5 %}
    """
    try:
        result = []
        for i, job in enumerate(jobs):
            result.append(job)
            if (i + 1) % n == 0 and i < len(jobs) - 1:
                # Marker special pentru a indica unde să fie inserată o reclamă
                result.append("__AD_PLACEHOLDER__")
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in inject_ad_every filter: {str(e)}")
        return jobs

@register.simple_tag(takes_context=True)
def render_lazy_ad(context, position):
    """
    Renders an ad that will be loaded only when it becomes visible in the viewport.
    This helps with performance by not loading ads that users may never see.
    
    Usage: {% render_lazy_ad 'position_name' %}
    """
    try:
        request = context.get('request')
        if not request:
            return ''
            
        # Return a placeholder that will be replaced with the actual ad when visible
        return mark_safe(
            f'<div class="lazy-ad-container" data-ad-position="{position}">'
            f'<div class="ad-placeholder bg-light p-3 text-center">'
            f'<small class="text-muted">Conținut se încarcă...</small>'
            f'</div></div>'
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error rendering lazy ad at position {position}: {str(e)}")
        return ''