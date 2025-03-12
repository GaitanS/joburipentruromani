from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# Import subscription models to make them available through models import
from .models_subscription import (
    SubscriptionPlan,
    CompanySubscription,
    SubscriptionPayment,
    StripeWebhookEvent
)

# Import blog models to make them available through models import
from .models_blog import (
    BlogCategory,
    BlogTag,
    BlogPost,
    BlogComment
)

class Category(models.Model):
    name = models.CharField(_('Nume'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True)
    icon = models.CharField(_('Iconiță CSS'), max_length=50, blank=True, help_text=_('Clasa CSS pentru iconiță'))
    job_count = models.PositiveIntegerField(_('Număr joburi'), default=0)
    
    class Meta:
        verbose_name = _('Categorie')
        verbose_name_plural = _('Categorii')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('jobs:category_detail', args=[self.slug])


class Location(models.Model):
    city = models.CharField(_('Oraș'), max_length=100)
    county = models.CharField(_('Județ'), max_length=100, blank=True)
    country = models.CharField(_('Țară'), max_length=100, default='România')
    
    class Meta:
        verbose_name = _('Locație')
        verbose_name_plural = _('Locații')
        ordering = ['city', 'county']
        unique_together = ('city', 'county')
    
    def __str__(self):
        if self.county and self.country:
            return f"{self.city}, {self.county}, {self.country}"
        else:
            return f"{self.city}, {self.country}"


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    name = models.CharField(_('Nume companie'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True)
    logo = models.ImageField(_('Logo'), upload_to='company_logos/', blank=True, null=True)
 
    description = models.TextField(_('Descriere'), blank=True)
    website = models.URLField(_('Website'), blank=True)
    founded_year = models.PositiveIntegerField(_('Anul înființării'), blank=True, null=True)
    employees = models.PositiveIntegerField(_('Număr angajați'), blank=True, null=True)
    is_featured = models.BooleanField(_('Este promovată'), default=False)
    
    def get_active_job_count(self):
        """Get count of active jobs for this company"""
        return self.jobs.filter(status='active').count()
    
    def can_post_job(self):
        """Check if company can post more jobs based on their subscription plan"""
        try:
            subscription = self.subscription
            if subscription.is_active():
                return subscription.can_post_more_jobs()
            return False
        except Exception:
            # If no subscription exists or any other error, default to no
            return False

    def can_promote_job(self):
        """Check if company can promote more jobs based on their subscription plan"""
        try:
            subscription = self.subscription
            if subscription.is_active():
                return subscription.remaining_promoted_listings() > 0
            return False
        except Exception:
            # If no subscription exists or any other error, default to no
            return False

    def get_job_visibility_days(self):
        """Get job visibility days based on subscription plan"""
        try:
            subscription = self.subscription
            if subscription.is_active():
                return subscription.plan.job_visibility_days
            return 30  # Default visibility
        except Exception:
            return 30  # Default visibility

    class Meta:
        verbose_name = _('Companie')
        verbose_name_plural = _('Companii')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('jobs:company_detail', args=[self.slug])


class Job(models.Model):
    STATUS_CHOICES = (
        ('active', _('Activ')),
        ('filled', _('Ocupat')),
        ('expired', _('Expirat')),
    )
    
    JOB_TYPE_CHOICES = (
        ('full_time', _('Full Time')),
        ('part_time', _('Part Time')),
        ('contract', _('Contract')),
        ('internship', _('Internship')),
        ('temporary', _('Temporar')),
    )
    
    EXPERIENCE_CHOICES = (
        ('entry', _('Entry level')),
        ('mid', _('Mid level')),
        ('senior', _('Senior level')),
        ('executive', _('Executive level')),
    )
    
    title = models.CharField(_('Titlu'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='jobs')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='jobs')
    job_type = models.CharField(_('Tip job'), max_length=20, choices=JOB_TYPE_CHOICES)
    experience = models.CharField(_('Experiență'), max_length=20, choices=EXPERIENCE_CHOICES, default='entry')
    description = models.TextField(_('Descriere'))
    requirements = models.TextField(_('Cerințe'))
    responsibilities = models.TextField(_('Responsabilități'))
    benefits = models.TextField(_('Beneficii'), blank=True)
    salary_min = models.DecimalField(_('Salariu minim'), max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(_('Salariu maxim'), max_digits=10, decimal_places=2, blank=True, null=True)
    is_featured = models.BooleanField(_('Este promovat'), default=False)
    is_remote = models.BooleanField(_('Remote'), default=False)
    status = models.CharField(_('Status'), max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(_('Creat la'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Actualizat la'), auto_now=True)
    expiry_date = models.DateField(_('Data expirării'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Job')
        verbose_name_plural = _('Joburi')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
        # Actualizăm numărul de joburi din categoria asociată
        self.category.job_count = Job.objects.filter(category=self.category, status='active').count()
        self.category.save()
    
    def get_absolute_url(self):
        return reverse('jobs:job_detail', args=[self.slug])


class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', _('În așteptare')),
        ('reviewed', _('Verificat')),
        ('interviewed', _('Intervievat')),
        ('hired', _('Angajat')),
        ('rejected', _('Respins')),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(_('CV'), upload_to='resumes/')
    cover_letter = models.TextField(_('Scrisoare de intenție'), blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(_('Creat la'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Actualizat la'), auto_now=True)
    
    class Meta:
        verbose_name = _('Aplicare')
        verbose_name_plural = _('Aplicări')
        ordering = ['-created_at']
        unique_together = ('job', 'user')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.job.title}"


class AdPlacement(models.Model):
    """
    Model pentru gestionarea reclamelor Google AdSense
    """
    POSITION_CHOICES = [
        ('header', _('Sub Header')),
        ('between_categories', _('Între Categorii și Joburi')),
        ('sidebar', _('Sidebar')),
        ('job_listing', _('Între Listări de Joburi')),
        ('job_detail', _('Sub Detalii Job')),
        ('footer', _('Footer')),
        ('user_dashboard', _('Dashboard Utilizator')),
        ('company_dashboard', _('Dashboard Companie')),
        ('after_apply', _('După Aplicare')),
        ('subscription_top', _('Pagini Abonament - Sus')),
        ('subscription_bottom', _('Pagini Abonament - Jos')),
        ('subscription_sidebar', _('Pagini Abonament - Sidebar')),
        ('subscription_success', _('Pagină Succes Abonament')),
    ]
    
    DEVICE_CHOICES = [
        ('all', _('Toate Dispozitivele')),
        ('desktop', _('Desktop')),
        ('tablet', _('Tabletă')),
        ('mobile', _('Mobil')),
    ]
    
    name = models.CharField(_('Nume'), max_length=100)
    position = models.CharField(_('Poziție'), max_length=50, choices=POSITION_CHOICES)
    ad_code = models.TextField(_('Cod reclamă'), help_text=_('Cod snippet Google AdSense'))
    is_active = models.BooleanField(_('Activ'), default=True)
    display_order = models.IntegerField(_('Ordine afișare'), default=0)
    target_devices = models.CharField(_('Dispozitive țintă'), max_length=20, choices=DEVICE_CHOICES, default='all')
    
    class Meta:
        ordering = ['display_order']
        verbose_name = _('Amplasare Reclamă')
        verbose_name_plural = _('Amplasări Reclame')
        
    def __str__(self):
        return f"{self.name} ({self.get_position_display()})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', blank=True, null=True)
    profession = models.CharField(_('Profesie'), max_length=100, blank=True)
    bio = models.TextField(_('Biografie'), blank=True)
    phone = models.CharField(_('Telefon'), max_length=20, blank=True)
    address = models.CharField(_('Adresă'), max_length=200, blank=True)
    resume = models.FileField(_('CV'), upload_to='resumes/', blank=True, null=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True)
    website = models.URLField(_('Website'), blank=True)
    
    class Meta:
        verbose_name = _('Profil Utilizator')
        verbose_name_plural = _('Profiluri Utilizatori')
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
