from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Job, Category, Company
from .models_blog import BlogPost, BlogCategory

class JobSitemap(Sitemap):
    """
    Sitemap for Job objects
    """
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Job.objects.filter(status='active')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

class CategorySitemap(Sitemap):
    """
    Sitemap for Category objects
    """
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()

class CompanySitemap(Sitemap):
    """
    Sitemap for Company objects
    """
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Company.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()

class BlogPostSitemap(Sitemap):
    """
    Sitemap for BlogPost objects
    """
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

class BlogCategorySitemap(Sitemap):
    """
    Sitemap for BlogCategory objects
    """
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return BlogCategory.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()

class StaticViewSitemap(Sitemap):
    """
    Sitemap for static pages
    """
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ['jobs:home', 'jobs:job_list', 'jobs:about', 'jobs:for_companies', 
                'jobs:terms', 'jobs:privacy', 'jobs:blog_home']

    def location(self, item):
        return reverse(item)