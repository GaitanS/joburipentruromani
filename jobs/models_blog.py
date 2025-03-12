from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.utils.html import strip_tags
from django.conf import settings

class BlogCategory(models.Model):
    """Blog category model for organizing blog posts"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    meta_title = models.CharField(max_length=150, blank=True, 
                                help_text="Title used for SEO (max 150 chars)")
    meta_description = models.CharField(max_length=160, blank=True, 
                                       help_text="Description used for SEO (max 160 chars)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('jobs:blog_category', kwargs={'slug': self.slug})


class BlogTag(models.Model):
    """Tags for blog posts to improve searchability and categorization"""
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=70, unique=True)
    
    class Meta:
        verbose_name = "Blog Tag"
        verbose_name_plural = "Blog Tags"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('jobs:blog_tag', kwargs={'slug': self.slug})


class BlogPost(models.Model):
    """Blog post model with SEO features and rich content"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, 
                           help_text="URL-friendly version of the title")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(BlogTag, blank=True, related_name='posts')
    
    # Content fields
    summary = models.TextField(help_text="Short summary shown in listings (max 250 chars)")
    content = RichTextField()
    featured_image = models.ImageField(upload_to='blog/%Y/%m/', blank=True, null=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=150, blank=True, 
                                 help_text="Custom title for SEO (max 150 chars)")
    meta_description = models.CharField(max_length=160, blank=True, 
                                       help_text="Custom description for SEO (max 160 chars)")
    meta_keywords = models.CharField(max_length=200, blank=True, 
                                    help_text="Comma-separated keywords for SEO")
    
    # Status and scheduling
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False, 
                                  help_text="Featured posts appear on homepage")
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Social sharing
    enable_comments = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-generate meta tags if not provided
        if not self.meta_title:
            self.meta_title = self.title[:150]
        
        if not self.meta_description:
            # Strip HTML tags for meta description
            plain_content = strip_tags(self.content)
            self.meta_description = plain_content[:157] + "..." if len(plain_content) > 160 else plain_content
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('jobs:blog_detail', kwargs={'slug': self.slug})
    
    @property
    def reading_time(self):
        """Estimate reading time based on content length"""
        word_count = len(strip_tags(self.content).split())
        minutes = word_count // 200  # Assuming 200 words per minute reading speed
        return max(1, minutes)  # Minimum 1 minute
    
    @property
    def is_published(self):
        """Check if post is published and publication date has passed"""
        return self.status == 'published' and self.published_at <= timezone.now()


class BlogComment(models.Model):
    """Comments for blog posts"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Blog Comment"
        verbose_name_plural = "Blog Comments"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"