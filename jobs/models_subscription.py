from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import stripe
from django.conf import settings
import uuid

# Initialize Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionPlan(models.Model):
    """Subscription plan model to define available tiers"""
    TIER_CHOICES = [
        ('free', _('Free')),
        ('standard', _('Standard')),
        ('business', _('Business')),
        ('enterprise', _('Enterprise')),
        ('promoted_only', _('Promoted Only')),
    ]
    
    BILLING_CYCLE_CHOICES = [
        ('monthly', _('Monthly')),
        ('annual', _('Annual')),
    ]
    
    tier = models.CharField(_('Tier'), max_length=20, choices=TIER_CHOICES)
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'))
    price_monthly = models.DecimalField(_('Monthly Price (EUR)'), max_digits=10, decimal_places=2)
    price_annually = models.DecimalField(_('Annual Price (EUR)'), max_digits=10, decimal_places=2)
    max_active_jobs = models.IntegerField(_('Maximum Active Job Listings'), default=1)
    job_visibility_days = models.IntegerField(_('Job Visibility Days'), default=30)
    has_candidate_cv_access = models.BooleanField(_('Candidate CV Access'), default=True)
    promoted_listings_count = models.IntegerField(_('Included Promoted Listings'), default=0)
    has_priority_support = models.BooleanField(_('Priority Support'), default=False)
    stripe_monthly_price_id = models.CharField(_('Stripe Monthly Price ID'), max_length=100, blank=True, null=True)
    stripe_annual_price_id = models.CharField(_('Stripe Annual Price ID'), max_length=100, blank=True, null=True)
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.IntegerField(_('Display Order'), default=0)
    
    class Meta:
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.get_tier_display()} - {self.name}"

    @property
    def is_free(self):
        return self.tier == 'free'

class CompanySubscription(models.Model):
    """Company subscription model tracking the active subscription for a company"""
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('past_due', _('Past Due')),
        ('canceled', _('Canceled')),
        ('trialing', _('Trialing')),
        ('expired', _('Expired')),
    ]
    
    BILLING_CYCLE_CHOICES = [
        ('monthly', _('Monthly')),
        ('annual', _('Annual')),
    ]
    
    company = models.OneToOneField('jobs.Company', on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
    stripe_customer_id = models.CharField(_('Stripe Customer ID'), max_length=100, blank=True, null=True)
    stripe_subscription_id = models.CharField(_('Stripe Subscription ID'), max_length=100, blank=True, null=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='active')
    billing_cycle = models.CharField(_('Billing Cycle'), max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    start_date = models.DateTimeField(_('Start Date'), default=timezone.now)
    end_date = models.DateTimeField(_('End Date'), null=True, blank=True)
    is_trial = models.BooleanField(_('Is Trial'), default=False)
    trial_end_date = models.DateTimeField(_('Trial End Date'), null=True, blank=True)
    auto_renew = models.BooleanField(_('Auto Renew'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Company Subscription')
        verbose_name_plural = _('Company Subscriptions')
        
    def __str__(self):
        return f"{self.company.name} - {self.plan.name} ({self.get_status_display()})"
        
    def is_active(self):
        """Check if the subscription is currently active"""
        return self.status == 'active' and (self.end_date is None or self.end_date > timezone.now())
        
    def active_jobs_count(self):
        """Count active job listings for this company"""
        from django.apps import apps
        Job = apps.get_model('jobs', 'Job')
        return Job.objects.filter(company=self.company, status='active').count()
        
    def can_post_more_jobs(self):
        """Check if the company can post more jobs based on their plan limits"""
        if not self.is_active():
            return False
        current_active_jobs = self.active_jobs_count()
        return current_active_jobs < self.plan.max_active_jobs or self.plan.max_active_jobs == -1
        
    def remaining_promoted_listings(self):
        """Calculate remaining promoted listings based on usage"""
        # Count the number of currently promoted active jobs
        from django.apps import apps
        Job = apps.get_model('jobs', 'Job')
        promoted_jobs_count = Job.objects.filter(
            company=self.company, 
            status='active',
            is_featured=True
        ).count()
        
        # Calculate remaining
        if self.plan.promoted_listings_count == 0:
            return 0
        return max(0, self.plan.promoted_listings_count - promoted_jobs_count)

    def days_remaining(self):
        """Calculate days remaining in current billing cycle"""
        if not self.end_date:
            return 0
        now = timezone.now()
        if now > self.end_date:
            return 0
        delta = self.end_date - now
        return delta.days
        
    def cancel_subscription(self):
        """Cancel subscription in Stripe and update status"""
        if self.stripe_subscription_id:
            try:
                stripe.Subscription.delete(self.stripe_subscription_id)
                self.status = 'canceled'
                self.auto_renew = False
                self.save()
                return True
            except Exception as e:
                # Log the error
                print(f"Error canceling subscription: {str(e)}")
                return False
        else:
            self.status = 'canceled'
            self.auto_renew = False
            self.save()
            return True

class SubscriptionPayment(models.Model):
    """Subscription payment tracking"""
    subscription = models.ForeignKey(CompanySubscription, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(_('Payment ID'), max_length=100, unique=True)
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('Currency'), max_length=3, default='EUR')
    status = models.CharField(_('Status'), max_length=20)
    payment_method = models.CharField(_('Payment Method'), max_length=50)
    payment_date = models.DateTimeField(_('Payment Date'), default=timezone.now)
    is_successful = models.BooleanField(_('Is Successful'), default=False)
    transaction_data = models.JSONField(_('Transaction Data'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Subscription Payment')
        verbose_name_plural = _('Subscription Payments')
        
    def __str__(self):
        return f"{self.subscription.company.name} - {self.amount} {self.currency} - {self.status}"

class StripeWebhookEvent(models.Model):
    """Store Stripe webhook events for tracking and audit"""
    webhook_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Stripe Webhook Event')
        verbose_name_plural = _('Stripe Webhook Events')
        
    def __str__(self):
        return f"{self.event_type} - {self.webhook_id}"