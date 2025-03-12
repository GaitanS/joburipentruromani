# JoburipentruRomani - Job Board Platform

A comprehensive job board platform built with Django, specifically designed for Romanian job seekers and employers, with strategic AdSense integration for revenue generation.

## Overview

JoburipentruRomani ("Jobs for Romanians") is a full-featured job board platform that connects Romanian job seekers with employers. The platform features job listings, company profiles, user accounts, application management, and strategic AdSense placements to generate revenue while maintaining excellent user experience.

## Features

- **User Accounts**: Registration and profiles for both job seekers and employers
- **Job Listings**: Comprehensive job postings with detailed information
- **Search & Filters**: Advanced search with multiple filtering options
- **Categories**: Job categorization for easy navigation
- **Application System**: Apply to jobs directly through the platform
- **Company Profiles**: Detailed company information pages
- **Dashboards**: Separate dashboards for users and companies
- **AdSense Integration**: Strategic ad placements throughout the site
- **Mobile Responsive**: Fully responsive design for all devices
- **SEO Optimized**: Built with search engine optimization in mind

## Installation

### Prerequisites

- Python 3.8+
- Django 5.0+
- PostgreSQL (recommended for production) or SQLite (development)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/joburipentruromani.git
   cd joburipentruromani
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Setup the database:
   ```
   python manage.py migrate
   ```

5. Load initial data:
   ```
   python manage.py loaddata jobs/fixtures/categories.json
   python manage.py loaddata jobs/fixtures/locations.json
   python manage.py loaddata jobs/fixtures/ad_placements.json
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Access the site at http://127.0.0.1:8000/ and the admin panel at http://127.0.0.1:8000/admin/

## AdSense Integration

The platform uses a flexible AdSense integration system that allows for:

1. **Strategic Ad Placement**: Ads are positioned in high-visibility, high-engagement areas
2. **Database-Driven Ad Management**: All ad placements are stored in the database and can be managed via the admin panel
3. **Template Tag System**: Custom template tags make it easy to insert ads in templates
4. **Responsive Ads**: All ad units adapt to different screen sizes

### Key Ad Placements

- Header banner (all pages)
- Between categories and job listings (homepage)
- In-feed ads (every 5 job listings)
- Sidebar ads (job listings, job details)
- Below job description (job detail pages)
- After application submission (confirmation pages)
- Footer ads (all pages)
- User/Company dashboard ads

### Using the Ad Template Tags

To add an ad to a template:

```html
{% load adsense %}

<!-- Basic ad placement -->
{% render_ad 'position_name' %}

<!-- Native ad that looks like a job listing -->
{% render_native_ad_job %}
```

See `jobs/templatetags/adsense.py` for implementation details.

## Directory Structure

```
joburipentruromani/
├── jobs/                   # Main app
│   ├── admin.py            # Admin panel configuration
│   ├── fixtures/           # Initial data fixtures
│   ├── migrations/         # Database migrations
│   ├── models.py           # Data models
│   ├── templatetags/       # Custom template tags (including adsense.py)
│   ├── urls.py             # URL routing for the app
│   └── views.py            # View controllers
├── joburipentruromani/     # Project settings
│   ├── settings.py         # Project settings
│   ├── urls.py             # Main URL routing
│   └── wsgi.py             # WSGI configuration
├── static/                 # Static files (CSS, JS, images)
│   ├── css/                # CSS stylesheets
│   ├── js/                 # JavaScript files
│   └── robots.txt          # SEO robots configuration
├── templates/              # HTML templates
│   ├── auth/               # Authentication templates
│   ├── jobs/               # Job-related templates
│   ├── base.html           # Base template
│   └── sitemaps/           # Sitemap templates
├── manage.py               # Django management script
├── backup_script.py        # Database backup script
├── create_superuser.py     # Utility to create admin user
└── adsense_implementation_plan.md  # Documentation of AdSense strategy
```

## AdSense Configuration

To configure your AdSense account:

1. Register with Google AdSense and get your publisher ID
2. In the Django admin panel, go to "Ad Placements"
3. Update each ad placement with your AdSense code (replace the placeholder client/slot IDs)
4. Ensure `is_active` is set to True for the placements you want to display

## Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure a production-ready database (PostgreSQL recommended)
3. Set up proper static file serving
4. Use a production web server (Nginx/Apache) with Gunicorn/uWSGI
5. Set up SSL for secure connections

## Backup System

The platform includes a backup script (`backup_script.py`) that can be set up as a cron job to regularly backup the database. Configure your database credentials in the script before use.

## License

[MIT License](LICENSE)

## Credits

- Bootstrap framework for responsive design
- Font Awesome for icons
- Django for the web framework