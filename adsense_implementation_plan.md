# AdSense Implementation Plan for JoburipentruRomani

## Overview

This document outlines the strategic implementation of Google AdSense across the JoburipentruRomani job board platform. The goal is to maximize ad revenue while maintaining excellent user experience, ensuring ads are placed in locations that have high visibility and interaction potential without disrupting the primary functions of the site.

## Ad Placements

We have identified the following strategic ad placements across the site:

### 1. Header Banner
- **Position**: Top of all pages, below the navigation bar
- **Size**: Responsive (728x90 on desktop, 320x100 on mobile)
- **Pages**: All pages
- **Priority**: High
- **Notes**: Premium position with high visibility

### 2. Between Categories and Job Listings
- **Position**: Between category section and job listings on homepage
- **Size**: Responsive (970x250 on desktop, 300x250 on mobile)
- **Pages**: Homepage only
- **Priority**: High
- **Notes**: Natural break point in content, high CTR potential

### 3. Sidebar Ads
- **Position**: Right sidebar
- **Size**: 300x600 (desktop only)
- **Pages**: Job listings, job details, category pages
- **Priority**: Medium
- **Notes**: Multiple sidebar ads can be placed with sufficient spacing

### 4. In-Feed Job Listings
- **Position**: After every 5 job listings
- **Size**: Responsive (same as job listing cards)
- **Pages**: Job listing pages, search results
- **Priority**: High
- **Notes**: Native-style ads that match the job listing format

### 5. Below Job Description
- **Position**: After job description, before application form
- **Size**: Responsive (728x90 on desktop, 300x250 on mobile)
- **Pages**: Job detail pages
- **Priority**: Very High
- **Notes**: High-intent users approaching application point

### 6. After Application Submission
- **Position**: Confirmation page after applying for a job
- **Size**: Responsive (970x250 on desktop, 300x250 on mobile)
- **Pages**: Application confirmation pages
- **Priority**: Very High
- **Notes**: Highly engaged users with high satisfaction moment

### 7. Footer Ads
- **Position**: Above footer
- **Size**: Responsive (970x90 on desktop, 320x100 on mobile)
- **Pages**: All pages
- **Priority**: Medium
- **Notes**: Visible to users who scroll to the bottom

### 8. User Dashboard
- **Position**: Sidebar of user/company dashboards
- **Size**: 300x250
- **Pages**: User dashboard, company dashboard
- **Priority**: Low
- **Notes**: Logged-in users, more targeted ads possible

## Native Ad Implementations

### 1. Sponsored Job Listings
- **Position**: Mixed with organic job listings, clearly marked as "Sponsored"
- **Pages**: Job listing pages, search results
- **Priority**: High
- **Notes**: Formatted exactly like regular job listings but with slight highlight

### 2. Recommended Jobs
- **Position**: "Similar jobs" section on job detail pages
- **Format**: Native ad format that resembles job cards
- **Priority**: Medium
- **Notes**: Relevant to the user's current job interests

## Implementation Strategy

### Phase 1: Initial Setup
1. Create AdSense account and get approval
2. Implement core ad placements (Header, Sidebar, In-Feed, Below Description)
3. Set up ad exclusion categories to prevent competitor ads
4. Implement responsive ad units for all placements

### Phase 2: Optimization
1. Analyze performance data after 2-4 weeks
2. A/B test different ad positions and formats
3. Implement lazy loading for below-the-fold ads
4. Optimize mobile ad experience

### Phase 3: Advanced Implementation
1. Implement native ad formats
2. Set up auto ads for additional placements
3. Explore premium placement opportunities
4. Implement personalized ad targeting

## Technical Implementation

We are using a custom Django template tag system to handle ad rendering:

```python
# jobs/templatetags/adsense.py
@register.simple_tag
def render_ad(position):
    """Renders AdSense code for a specific position"""
    try:
        ad = AdPlacement.objects.get(position=position, is_active=True)
        return mark_safe(ad.ad_code)
    except AdPlacement.DoesNotExist:
        return ''
```

This allows for:
- Easy management of ad placements in the database
- A/B testing different ad sizes and formats
- Conditional rendering based on user status or page context
- Quick enabling/disabling of specific ad positions

## Performance Monitoring

- Set up regular reporting on ad performance
- Monitor key metrics: CTR, RPM, fill rate, viewability
- Track user experience metrics to ensure ads don't impact site usability
- Implement heatmap tracking to identify optimal placement opportunities

## Ad Revenue Projection

Based on industry benchmarks for job boards:
- Average CTR: 0.2% - 0.5%
- Average CPC: $0.30 - $0.80
- Estimated monthly page views: 100,000+
- Projected monthly revenue: $200 - $800 (initial phase)

## Compliance Considerations

- All ads clearly distinguished from content
- Privacy policy updated to address ad personalization
- Cookie consent implementation for GDPR compliance
- Ads excluded from sensitive areas (application forms, login screens)
- Ad density maintained below Google's recommended limits

## Future Enhancements

- Custom channel setup for specific placements
- AdSense Auto ads experiment for discovering new placements
- Direct deals with relevant employment/recruitment advertisers
- AdSense for Search implementation for job search results