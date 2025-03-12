from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models_subscription import (
    SubscriptionPlan, 
    CompanySubscription, 
    SubscriptionPayment,
    StripeWebhookEvent
)

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'price_monthly', 'price_annually', 'max_active_jobs', 
                   'job_visibility_days', 'promoted_listings_count', 'is_active', 'order')
    list_filter = ('tier', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('order',)
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('tier', 'name', 'description', 'is_active', 'order')
        }),
        (_('Pricing'), {
            'fields': ('price_monthly', 'price_annually', 'stripe_monthly_price_id', 'stripe_annual_price_id')
        }),
        (_('Features'), {
            'fields': ('max_active_jobs', 'job_visibility_days', 'has_candidate_cv_access', 
                      'promoted_listings_count', 'has_priority_support')
        }),
    )

@admin.register(CompanySubscription)
class CompanySubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company', 'plan', 'status', 'billing_cycle', 'start_date', 'end_date', 
                   'is_active_display', 'auto_renew')
    list_filter = ('status', 'billing_cycle', 'auto_renew')
    search_fields = ('company__name', 'stripe_customer_id', 'stripe_subscription_id')
    raw_id_fields = ('company', 'plan')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (_('Subscription Information'), {
            'fields': ('company', 'plan', 'status', 'billing_cycle', 'start_date', 'end_date', 'auto_renew')
        }),
        (_('Stripe Information'), {
            'fields': ('stripe_customer_id', 'stripe_subscription_id')
        }),
        (_('Trial Information'), {
            'fields': ('is_trial', 'trial_end_date'),
            'classes': ('collapse',)
        }),
    )
    
    def is_active_display(self, obj):
        if obj.is_active():
            return format_html('<span style="color: green;">●</span> Active')
        return format_html('<span style="color: red;">●</span> Inactive')
    is_active_display.short_description = _('Is Active')
    
    actions = ['cancel_subscriptions']
    
    def cancel_subscriptions(self, request, queryset):
        canceled_count = 0
        for subscription in queryset:
            if subscription.cancel_subscription():
                canceled_count += 1
        
        if canceled_count:
            self.message_user(request, _('%d subscriptions have been canceled.') % canceled_count)
    cancel_subscriptions.short_description = _('Cancel selected subscriptions')

@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'payment_id', 'amount', 'currency', 'status', 
                   'payment_method', 'payment_date', 'is_successful')
    list_filter = ('status', 'payment_method', 'is_successful', 'currency')
    search_fields = ('payment_id', 'subscription__company__name')
    date_hierarchy = 'payment_date'
    raw_id_fields = ('subscription',)
    
    fieldsets = (
        (_('Payment Information'), {
            'fields': ('subscription', 'payment_id', 'amount', 'currency', 'status', 
                      'payment_method', 'payment_date', 'is_successful')
        }),
        (_('Transaction Data'), {
            'fields': ('transaction_data',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('payment_id', 'transaction_data')

@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = ('webhook_id', 'event_type', 'processed', 'created_at')
    list_filter = ('event_type', 'processed')
    search_fields = ('webhook_id', 'event_type')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Event Information'), {
            'fields': ('webhook_id', 'event_type', 'processed')
        }),
        (_('Event Data'), {
            'fields': ('event_data',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('webhook_id', 'event_type', 'event_data')