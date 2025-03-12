from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.template import Template, Context
from django.utils.safestring import SafeString

from .models import AdPlacement, Category, Company, Location, Job, UserProfile, Application
from .templatetags.adsense import render_ad, render_native_ad_job


class AdPlacementModelTest(TestCase):
    def setUp(self):
        self.ad_placement = AdPlacement.objects.create(
            name="Test Header Ad",
            position="header",
            ad_code="<div>Test Ad</div>",
            is_active=True,
            display_order=1,
            target_devices="all"
        )
    
    def test_ad_placement_creation(self):
        """Test AdPlacement object creation"""
        self.assertEqual(self.ad_placement.name, "Test Header Ad")
        self.assertEqual(self.ad_placement.position, "header")
        self.assertEqual(self.ad_placement.ad_code, "<div>Test Ad</div>")
        self.assertTrue(self.ad_placement.is_active)
        self.assertEqual(self.ad_placement.display_order, 1)
        self.assertEqual(self.ad_placement.target_devices, "all")
    
    def test_string_representation(self):
        """Test AdPlacement string representation"""
        # Modify this to match the actual string representation in our model
        self.assertEqual(str(self.ad_placement), f"{self.ad_placement.name}")


class AdsenseTemplateTagsTest(TestCase):
    def setUp(self):
        self.active_ad = AdPlacement.objects.create(
            name="Active Ad",
            position="header",
            ad_code="<div>Active Ad</div>",
            is_active=True
        )
        
        self.inactive_ad = AdPlacement.objects.create(
            name="Inactive Ad",
            position="footer",
            ad_code="<div>Inactive Ad</div>",
            is_active=False
        )
    
    def test_render_ad_tag_active(self):
        """Test rendering an active ad placement"""
        # Create a mock context if needed
        context = {}
        result = render_ad(context, "header")
        self.assertIsInstance(result, SafeString)
        self.assertEqual(result, "<div>Active Ad</div>")
    
    def test_render_ad_tag_inactive(self):
        """Test rendering an inactive ad placement"""
        context = {}
        result = render_ad(context, "footer")
        self.assertEqual(result, "")
    
    def test_render_ad_tag_nonexistent(self):
        """Test rendering a non-existent ad placement"""
        context = {}
        result = render_ad(context, "nonexistent")
        self.assertEqual(result, "")
    
    def test_render_native_ad_job(self):
        """Test rendering a native job ad"""
        context = {}
        result = render_native_ad_job(context)
        self.assertIsInstance(result, SafeString)
        self.assertIn("Sponsorizat", result)  # Checking for Romanian word for "Sponsored"


class AdRenderingViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test user for company
        self.test_user = User.objects.create_user(
            username='testemployer',
            email='employer@example.com',
            password='testpassword123'
        )
        
        # Create an active ad
        self.header_ad = AdPlacement.objects.create(
            name="Header Ad",
            position="header",
            ad_code="<div id='test-header-ad'>Header Ad</div>",
            is_active=True
        )
        
        # Create sample data
        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category",
            icon="fas fa-test",
            job_count=5
        )
        
        self.location = Location.objects.create(
            city="Test City",
            county="Test County"
        )
        
        # Add user to company model
        self.company = Company.objects.create(
            name="Test Company",
            slug="test-company",
            website="https://example.com",
            description="Test company description",
            user=self.test_user  # Required user field
        )
        
        self.job = Job.objects.create(
            title="Test Job",
            slug="test-job",
            company=self.company,
            location=self.location,
            category=self.category,
            description="Test job description",
            requirements="Test job requirements",
            is_active=True
        )
    
    def test_home_page_ad_rendering(self):
        """Test that ads are rendered on the home page"""
        response = self.client.get(reverse('jobs:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test-header-ad")
    
    def test_job_list_page_ad_rendering(self):
        """Test that ads are rendered on the job list page"""
        response = self.client.get(reverse('jobs:job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test-header-ad")
    
    def test_job_detail_page_ad_rendering(self):
        """Test that ads are rendered on the job detail page"""
        response = self.client.get(reverse('jobs:job_detail', args=[self.job.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test-header-ad")


class UserBasedAdTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='testpassword123'
        )
        
        self.premium_user = User.objects.create_user(
            username='premiumuser',
            email='premium@example.com',
            password='testpassword123'
        )
        
        # Create user profiles - adjust fields based on our actual model
        self.regular_profile = UserProfile.objects.create(
            user=self.regular_user,
            phone="0123456789"
            # Remove is_premium if it doesn't exist
        )
        
        self.premium_profile = UserProfile.objects.create(
            user=self.premium_user,
            phone="0123456789"
            # Remove is_premium if it doesn't exist
        )
        
        # Create ad placements
        self.user_dashboard_ad = AdPlacement.objects.create(
            name="User Dashboard Ad",
            position="user_dashboard",
            ad_code="<div id='user-dashboard-ad'>User Dashboard Ad</div>",
            is_active=True
        )
    
    def test_regular_user_sees_ads(self):
        """Test that regular users see ads"""
        self.client.login(username='regularuser', password='testpassword123')
        
        # Modify this to match an actual URL in our application
        response = self.client.get(reverse('jobs:home'))  # Use a working URL
        self.assertEqual(response.status_code, 200)
        # This assertion might need to be changed based on how ads appear
        self.assertContains(response, "user-dashboard-ad")
    
    def test_premium_user_ad_visibility(self):
        """
        This is a placeholder test for premium user ad visibility.
        In a real implementation, we would check if premium users
        see fewer ads or no ads at all depending on the business logic.
        """
        # For now, we'll just check page loads correctly
        self.client.login(username='premiumuser', password='testpassword123')
        
        # Modify this to match an actual URL in our application
        response = self.client.get(reverse('jobs:home'))  # Use a working URL
        self.assertEqual(response.status_code, 200)


class MobileAdRenderingTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create mobile-specific and desktop-specific ads
        self.mobile_ad = AdPlacement.objects.create(
            name="Mobile Ad",
            position="mobile_header",
            ad_code="<div id='mobile-ad'>Mobile Ad</div>",
            is_active=True,
            target_devices="mobile"
        )
        
        self.desktop_ad = AdPlacement.objects.create(
            name="Desktop Ad",
            position="desktop_header",
            ad_code="<div id='desktop-ad'>Desktop Ad</div>",
            is_active=True,
            target_devices="desktop"
        )
        
        self.all_devices_ad = AdPlacement.objects.create(
            name="All Devices Ad",
            position="all_header",
            ad_code="<div id='all-devices-ad'>All Devices Ad</div>",
            is_active=True,
            target_devices="all"
        )
    
    def test_mobile_user_agent(self):
        """Test ad rendering with a mobile user agent"""
        # Set a mobile user agent
        mobile_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        }
        
        # This is a placeholder test. In a real implementation, we would check
        # if the correct ads are rendered based on the user agent.
        # For now, we'll just test that the page loads correctly
        response = self.client.get(reverse('jobs:home'), **mobile_headers)
        self.assertEqual(response.status_code, 200)
    
    def test_desktop_user_agent(self):
        """Test ad rendering with a desktop user agent"""
        # Set a desktop user agent
        desktop_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # This is a placeholder test. In a real implementation, we would check
        # if the correct ads are rendered based on the user agent.
        # For now, we'll just test that the page loads correctly
        response = self.client.get(reverse('jobs:home'), **desktop_headers)
        self.assertEqual(response.status_code, 200)
