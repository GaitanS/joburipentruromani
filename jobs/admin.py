from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Category, Location, Company, Job, Application, AdPlacement, UserProfile
from .models_subscription import (
    SubscriptionPlan, 
    CompanySubscription, 
    SubscriptionPayment,
    StripeWebhookEvent
)
# Import subscription admin
from .admin_subscription import (
    SubscriptionPlanAdmin,
    CompanySubscriptionAdmin,
    SubscriptionPaymentAdmin,
    StripeWebhookEventAdmin
)

class JoburiPentruRomaniAdminSite(admin.AdminSite):
    site_title = _('JoburiPentruRomani Admin')
    site_header = _('JoburiPentruRomani Administration')
    index_title = _('Site Administration')

# Create instance of custom admin site
admin_site = JoburiPentruRomaniAdminSite(name='admin')

# Register your models with the custom admin site
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    # Add custom list actions
    actions = ['reset_job_count']
    
    def reset_job_count(self, request, queryset):
        for category in queryset:
            category.job_count = category.job_set.count()
            category.save()
    reset_job_count.short_description = _("Reset job count for selected categories")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'county')
    search_fields = ('city', 'county')
    list_filter = ('county',)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('is_featured',)
    readonly_fields = ('user',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'job_type', 'status', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description', 'company__name', 'location__city')
    list_filter = ('status', 'job_type', 'experience', 'is_featured', 'is_remote', 'category')
    date_hierarchy = 'created_at'
    fieldsets = (
        (_('Informații de bază'), {
            'fields': ('title', 'slug', 'company', 'category', 'location', 'job_type', 'experience')
        }),
        (_('Detalii job'), {
            'fields': ('description', 'requirements', 'responsibilities', 'benefits')
        }),
        (_('Informații salariale'), {
            'fields': ('salary_min', 'salary_max')
        }),
        (_('Statusuri'), {
            'fields': ('status', 'is_featured', 'is_remote', 'expiry_date')
        }),
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('job__title', 'user__username', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'
    readonly_fields = ('job', 'user', 'resume', 'cover_letter', 'created_at')


@admin.register(AdPlacement)
class AdPlacementAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'is_active', 'target_devices', 'display_order')
    list_filter = ('position', 'is_active', 'target_devices')
    search_fields = ('name',)
    list_editable = ('is_active', 'display_order')
    fieldsets = (
        (_('Informații de bază'), {
            'fields': ('name', 'position', 'is_active')
        }),
        (_('Configurare Ad'), {
            'fields': ('ad_code', 'target_devices', 'display_order')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profession', 'phone')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'profession')
    readonly_fields = ('user',)
