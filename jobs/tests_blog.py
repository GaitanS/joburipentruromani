from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models_blog import BlogCategory, BlogTag, BlogPost, BlogComment

class BlogModelTests(TestCase):
    """
    Tests for blog-related models
    """
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='password123'
        )
        
        # Create a test category
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='A test category',
            meta_title='Test Category Title',
            meta_description='Test Category Description'
        )
        
        # Create a test tag
        self.tag = BlogTag.objects.create(
            name='Test Tag',
            slug='test-tag'
        )
        
        # Create a published post
        self.published_post = BlogPost.objects.create(
            title='Test Published Post',
            slug='test-published-post',
            author=self.user,
            category=self.category,
            summary='This is a test published post',
            content='<p>This is the content of a test published post.</p>',
            status='published',
            published_at=timezone.now() - timedelta(days=1)
        )
        self.published_post.tags.add(self.tag)
        
        # Create a draft post
        self.draft_post = BlogPost.objects.create(
            title='Test Draft Post',
            slug='test-draft-post',
            author=self.user,
            category=self.category,
            summary='This is a test draft post',
            content='<p>This is the content of a test draft post.</p>',
            status='draft',
            published_at=timezone.now() + timedelta(days=1)
        )
        
        # Create a comment
        self.comment = BlogComment.objects.create(
            post=self.published_post,
            name='Test Commenter',
            email='commenter@example.com',
            content='This is a test comment.',
            approved=True
        )
    
    def test_category_creation(self):
        """Test category model creation and string representation"""
        self.assertEqual(str(self.category), 'Test Category')
        self.assertEqual(self.category.get_absolute_url(), '/blog/category/test-category/')
    
    def test_tag_creation(self):
        """Test tag model creation and string representation"""
        self.assertEqual(str(self.tag), 'Test Tag')
        self.assertEqual(self.tag.get_absolute_url(), '/blog/tag/test-tag/')
    
    def test_blog_post_creation(self):
        """Test blog post model creation and string representation"""
        self.assertEqual(str(self.published_post), 'Test Published Post')
        self.assertEqual(self.published_post.get_absolute_url(), '/blog/test-published-post/')
        self.assertTrue(self.published_post.is_published)
        self.assertFalse(self.draft_post.is_published)
    
    def test_reading_time(self):
        """Test reading time calculation"""
        # Add more content to test reading time calculation
        self.published_post.content = '<p>' + 'Lorem ipsum ' * 200 + '</p>'
        self.published_post.save()
        
        # Reading time should be at least 1 minute
        self.assertGreaterEqual(self.published_post.reading_time, 1)
    
    def test_comment_creation(self):
        """Test comment model creation and string representation"""
        expected_str = f"Comment by {self.comment.name} on {self.published_post.title}"
        self.assertEqual(str(self.comment), expected_str)
        self.assertTrue(self.comment.approved)


class BlogViewTests(TestCase):
    """
    Tests for blog-related views
    """
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='password123'
        )
        
        # Create a staff user for admin views
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='password123',
            is_staff=True
        )
        
        # Create a test category
        self.category = BlogCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='A test category'
        )
        
        # Create a test tag
        self.tag = BlogTag.objects.create(
            name='Test Tag',
            slug='test-tag'
        )
        
        # Create some published posts
        for i in range(3):
            post = BlogPost.objects.create(
                title=f'Test Post {i}',
                slug=f'test-post-{i}',
                author=self.user,
                category=self.category,
                summary=f'This is test post {i}',
                content=f'<p>This is the content of test post {i}.</p>',
                status='published',
                published_at=timezone.now() - timedelta(days=i)
            )
            post.tags.add(self.tag)
        
        # Create a draft post
        self.draft_post = BlogPost.objects.create(
            title='Draft Post',
            slug='draft-post',
            author=self.user,
            category=self.category,
            summary='This is a draft post',
            content='<p>This is the content of a draft post.</p>',
            status='draft'
        )
        
        # Create a future post
        self.future_post = BlogPost.objects.create(
            title='Future Post',
            slug='future-post',
            author=self.user,
            category=self.category,
            summary='This is a future post',
            content='<p>This is the content of a future post.</p>',
            status='published',
            published_at=timezone.now() + timedelta(days=1)
        )
    
    def test_blog_home_view(self):
        """Test blog home view"""
        response = self.client.get(reverse('jobs:blog_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_home.html')
        
        # Should only show published posts (3 test posts)
        self.assertEqual(len(response.context['posts']), 3)
        
        # Draft and future posts should not be included
        for post in response.context['posts']:
            self.assertNotEqual(post.slug, 'draft-post')
            self.assertNotEqual(post.slug, 'future-post')
    
    def test_blog_category_view(self):
        """Test blog category view"""
        response = self.client.get(reverse('jobs:blog_category', args=['test-category']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_category.html')
        self.assertEqual(response.context['category'], self.category)
        
        # Should only show published posts in this category
        self.assertEqual(len(response.context['posts']), 3)
    
    def test_blog_tag_view(self):
        """Test blog tag view"""
        response = self.client.get(reverse('jobs:blog_tag', args=['test-tag']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_tag.html')
        self.assertEqual(response.context['tag'], self.tag)
        
        # Should only show published posts with this tag
        self.assertEqual(len(response.context['posts']), 3)
    
    def test_blog_detail_view_published(self):
        """Test blog detail view for a published post"""
        response = self.client.get(reverse('jobs:blog_detail', args=['test-post-0']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_detail.html')
        self.assertEqual(response.context['post'].title, 'Test Post 0')
    
    def test_blog_detail_view_draft(self):
        """Test blog detail view for a draft post (should 404)"""
        response = self.client.get(reverse('jobs:blog_detail', args=['draft-post']))
        self.assertEqual(response.status_code, 404)
    
    def test_blog_detail_view_future(self):
        """Test blog detail view for a future post (should 404)"""
        response = self.client.get(reverse('jobs:blog_detail', args=['future-post']))
        self.assertEqual(response.status_code, 404)
    
    def test_blog_search_view(self):
        """Test blog search view"""
        response = self.client.get(reverse('jobs:blog_search'), {'q': 'Test Post'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_search.html')
        
        # Should find all published posts with "Test Post" in title
        self.assertEqual(len(response.context['posts']), 3)
        
        # Empty search should return no results
        response = self.client.get(reverse('jobs:blog_search'), {'q': ''})
        self.assertEqual(len(response.context['posts']), 0)
    
    def test_blog_admin_access(self):
        """Test blog admin views access restrictions"""
        admin_urls = [
            reverse('jobs:blog_admin'),
            reverse('jobs:blog_create'),
            reverse('jobs:blog_comments_admin')
        ]
        
        # Anonymous user should be redirected to login
        for url in admin_urls:
            response = self.client.get(url)
            self.assertRedirects(response, f'/login/?next={url}')
        
        # Regular user should get permission denied
        self.client.login(username='testuser', password='password123')
        for url in admin_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)
        
        # Staff user should have access
        self.client.login(username='staffuser', password='password123')
        for url in admin_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)